from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import math
from os import path
import re
import random
import smtplib
import socket
import string
import uuid

from peewee import fn
import peewee
import tornado.web
import tornado

import db
import handlers
import settings
from modules.browser import utils

def build_dataset_structure(dataset_version, user=None, dataset=None):
    if dataset is None:
        dataset = dataset_version.dataset
    row = db.build_dict_from_row(dataset)

    row['version'] = db.build_dict_from_row(dataset_version)
    row['version']['available_from'] = row['version']['available_from'].strftime('%Y-%m-%d')

    row['has_image'] = dataset.has_image()

    if user:
        row['is_admin'] = user.is_admin(dataset)
        if user.has_access(dataset, dataset_version.version):
            row['authorization_level'] = 'has_access'
        elif user.has_requested_access(dataset):
            row['authorization_level'] = 'has_requested_access'
        else:
            row['authorization_level'] = 'no_access'

    return row


class QuitHandler(handlers.UnsafeHandler):
    def get(self):  # pylint: disable=no-self-use
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.stop()


class GetSchema(handlers.UnsafeHandler):
    """
    Returns the schema.org, and bioschemas.org, annotation for a given
    url.

    This function behaves quite differently from the rest of the application as
    the structured data testing tool had trouble catching the schema inject
    when it went through AngularJS. The solution for now has been to make this
    very general function that "re-parses" the 'url' request parameter to
    figure out what information to return.
    """
    def get(self):
        dataset = None
        version = None
        beacon = None
        try:
            url = self.get_argument('url')  # pylint: disable=no-value-for-parameter
            match = re.match(".*/dataset/([^/]+)(/version/([^/]+))?", url)
            if match:
                dataset = match.group(1)
                version = match.group(3)
            beacon = re.match(".*/dataset/.*/beacon", url)
        except tornado.web.MissingArgumentError:
            pass

        base = {"@context": "http://schema.org/",
                "@type": "DataCatalog",
                "name": "SweFreq",
                "alternateName": ["The Swedish Frequency resource for genomics"],
                "description": ("The Swedish Frequency resource for genomics (SweFreq) is a " +
                                "website developed to make genomic datasets more findable and " +
                                "accessible in order to promote collaboration, new research and " +
                                "increase public benefit."),
                "url": "https://swefreq.nbis.se/",
                "provider": {
                    "@type": "Organization",
                    "name": "National Bioinformatics Infrastructure Sweden",
                    "alternateName": ["NBIS",
                                      "ELIXIR Sweden"],
                    "logo": "http://nbis.se/assets/img/logos/nbislogo-green.svg",
                    "url": "https://nbis.se/"
                },
                "datePublished": "2016-12-23",
                "dateModified": "2017-02-01",
                "license": {
                    "@type": "CreativeWork",
                    "name": "GNU General Public License v3.0",
                    "url": "https://www.gnu.org/licenses/gpl-3.0.en.html"
                }}

        if dataset:
            dataset_schema = {'@type': "Dataset"}

            dataset_version = db.get_dataset_version(dataset, version)
            if dataset_version is None:
                self.send_error(status_code=404)
                return

            if dataset_version.available_from > datetime.now():
                # If it's not available yet, only return if user is admin.
                if not (self.current_user and
                        self.current_user.is_admin(dataset_version.dataset)):
                    self.send_error(status_code=403)
                    return

            base_url = "%s://%s" % (self.request.protocol, self.request.host)
            dataset_schema['url'] = base_url + "/dataset/" + dataset_version.dataset.short_name
            dataset_schema['@id'] = dataset_schema['url']
            dataset_schema['name'] = dataset_version.dataset.short_name
            dataset_schema['description'] = dataset_version.description
            dataset_schema['identifier'] = dataset_schema['name']
            dataset_schema['citation'] = dataset_version.ref_doi

            base["dataset"] = dataset_schema

        if beacon:
            base = {"@context": "http://schema.org",
                    # or maybe "se.nbis.swefreq" as in the beacon api?
                    "@id": "https://swefreq.nbis.se/api/beacon-elixir/",
                    "@type": "Beacon",
                    "dataset": [dataset_schema],
                    "dct:conformsTo": "https://bioschemas.org/specifications/drafts/Beacon/",
                    "name": "Swefreq Beacon",
                    "provider": base["provider"],
                    "supportedRefs": ["GRCh37"],
                    "description": "Beacon API Web Server based on the GA4GH Beacon API",
                    "version": "1.1.0",  # beacon api version
                    "aggregator": False,
                    "url": "https://swefreq.nbis.se/api/beacon-elixir/"}

        self.finish(base)


class ListDatasets(handlers.UnsafeHandler):
    def get(self):
        # List all datasets available to the current user, earliear than now OR
        # versions that are available in the future that the user is admin of.
        user = self.current_user

        ret = []
        if user:
            futures = (db.DatasetVersion.select()
                       .join(db.Dataset)
                       .join(db.DatasetAccess)
                       .where(db.DatasetVersion.available_from > datetime.now(),
                              db.DatasetAccess.user == user,
                              db.DatasetAccess.is_admin))
            for fut in futures:
                dataset = build_dataset_structure(fut, user)
                dataset['future'] = True
                ret.append(dataset)

        for version in db.DatasetVersionCurrent.select():
            dataset = build_dataset_structure(version, user)
            dataset['current'] = True
            ret.append(dataset)

        self.finish({'data': ret})


class GetDataset(handlers.UnsafeHandler):
    def get(self, dataset, version=None):
        dataset, version = utils.parse_dataset(dataset, version)
        user = self.current_user

        future_version = False

        version = db.get_dataset_version(dataset, version)
        if version is None:
            self.send_error(status_code=404)
            return

        if version.available_from > datetime.now():
            future_version = True

        ret = build_dataset_structure(version, user)
        ret['version']['var_call_ref'] = version.reference_set.reference_build
        ret['future'] = future_version

        self.finish(ret)


class ListDatasetVersions(handlers.UnsafeHandler):
    def get(self, dataset):
        dataset, _ = utils.parse_dataset(dataset)
        user = self.current_user
        dataset = db.get_dataset(dataset)

        versions = (db.DatasetVersion.select(db.DatasetVersion.version,
                                             db.DatasetVersion.available_from)
                    .where(db.DatasetVersion.dataset == dataset))
        logging.info("ListDatasetVersions")
        data = []
        found_current = False
        versions = sorted(versions, key=lambda version: version.version)
        for ver in reversed(versions):
            current = False
            future = False

            # Skip future versions unless admin
            if ver.available_from > datetime.now():
                if not (user and user.is_admin(dataset)):
                    continue
                future = True

            # Figure out if this is the current version
            if not found_current and ver.available_from < datetime.now():
                found_current = True
                current = True

            data.insert(0, {'name': ver.version,
                            'available_from': ver.available_from.strftime('%Y-%m-%d'),
                            'current': current,
                            'future': future})

        self.finish({'data': data})


class GenerateTemporaryLink(handlers.AuthorizedHandler):
    def post(self, dataset, ds_version=None):
        dataset, ds_version = utils.parse_dataset(dataset, ds_version)
        user = self.current_user
        dataset_version = db.get_dataset_version(dataset, ds_version)
        if dataset_version is None:
            self.send_error(status_code=404)
            return

        link_hash = db.Linkhash.create(user=user,
                                       dataset_version=dataset_version,
                                       hash=uuid.uuid4().hex,
                                       expires_on=datetime.now() + timedelta(hours=3))

        try:
            (db.Linkhash.delete()
             .where(db.Linkhash.expires_on < datetime.now())
             .execute())
        except peewee.OperationalError as err:
            logging.error(f"Could not clean old linkhashes: {err}")

        self.finish({'hash': link_hash.hash,
                     'expires_on': link_hash.expires_on.strftime("%Y-%m-%d %H:%M")})  # pylint: disable=no-member


class DatasetFiles(handlers.AuthorizedHandler):
    def get(self, dataset, ds_version=None):
        dataset, ds_version = utils.parse_dataset(dataset, ds_version)
        dataset_version = db.get_dataset_version(dataset, ds_version)
        if dataset_version is None:
            self.send_error(status_code=404)
            return

        ret = []
        for dv_file in dataset_version.files:
            file_dict = db.build_dict_from_row(dv_file)
            file_dict['dirname'] = path.dirname(file_dict['uri'])
            file_dict['human_size'] = format_bytes(file_dict['file_size'])
            ret.append(file_dict)

        self.finish({'files': ret})


def format_bytes(nbytes):
    postfixes = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb']
    exponent = math.floor(math.log(nbytes) / math.log(1000))
    return f"{round(nbytes/1000**exponent, 2)} {postfixes[exponent]}"


class Collection(handlers.UnsafeHandler):
    def get(self, dataset, ds_version=None):
        del ds_version
        dataset, _ = utils.parse_dataset(dataset)
        dataset = db.get_dataset(dataset)

        collections = {}

        for sample_set in dataset.sample_sets:
            collection = sample_set.collection
            if collection.name not in collections:
                collections[collection.name] = {'sample_sets': [],
                                                'ethnicity': collection.ethnicity}
            collections[collection.name]['sample_sets'].append(db.build_dict_from_row(sample_set))

        ret = {
            'collections': collections,
            'study': db.build_dict_from_row(dataset.study)
        }
        ret['study']['publication_date'] = ret['study']['publication_date'].strftime('%Y-%m-%d')

        self.finish(ret)


class GetUser(handlers.UnsafeHandler):
    def get(self):
        user = self.current_user

        ret = {'user': None, 'email': None, 'login_type': 'none'}
        if user:
            ret = {'user': user.name,
                   'email': user.email,
                   'affiliation': user.affiliation,
                   'country': user.country}

        self.finish(ret)


class CountryList(handlers.UnsafeHandler):
    def get(self):
        self.write({'countries': [{'name': c} for c in self.country_list]})

    @property
    def country_list(self):
        return ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra",
                "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda",
                "Argentina", "Armenia", "Aruba", "Australia", "Austria",
                "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados",
                "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan",
                "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
                "British Indian Ocean Territory", "British Virgin Islands",
                "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia",
                "Cameroon", "Canada", "Cape Verde", "Cayman Islands",
                "Central African Republic", "Chad", "Chile", "China",
                "Christmas Island", "Cocos Islands", "Colombia", "Comoros",
                "Cook Islands", "Costa Rica", "Croatia", "Cuba", "Curacao",
                "Cyprus", "Czech Republic", "Democratic Republic of the Congo",
                "Denmark", "Djibouti", "Dominica", "Dominican Republic",
                "East Timor", "Ecuador", "Egypt", "El Salvador",
                "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia",
                "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France",
                "French Polynesia", "Gabon", "Gambia", "Georgia", "Germany",
                "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guam",
                "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana",
                "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India",
                "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel",
                "Italy", "Ivory Coast", "Jamaica", "Japan", "Jersey", "Jordan",
                "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait",
                "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia",
                "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau",
                "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives",
                "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius",
                "Mayotte", "Mexico", "Micronesia", "Moldova", "Monaco",
                "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique",
                "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands",
                "Netherlands Antilles", "New Caledonia", "New Zealand",
                "Nicaragua", "Niger", "Nigeria", "Niue", "North Korea",
                "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau",
                "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru",
                "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico",
                "Qatar", "Republic of the Congo", "Reunion", "Romania", "Russia",
                "Rwanda", "Saint Barthelemy", "Saint Helena",
                "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin",
                "Saint Pierre and Miquelon",
                "Saint Vincent and the Grenadines", "Samoa", "San Marino",
                "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
                "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten",
                "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
                "South Africa", "South Korea", "South Sudan", "Spain",
                "Sri Lanka", "Sudan", "Suriname", "Svalbard and Jan Mayen",
                "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan",
                "Tajikistan", "Tanzania", "Thailand", "Togo", "Tokelau", "Tonga",
                "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
                "Turks and Caicos Islands", "Tuvalu", "U.S. Virgin Islands",
                "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
                "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican",
                "Venezuela", "Vietnam", "Wallis and Futuna", "Western Sahara",
                "Yemen", "Zambia", "Zimbabwe"]


class RequestAccess(handlers.SafeHandler):
    def post(self, dataset):
        dataset, _ = utils.parse_dataset(dataset)
        user = self.current_user
        dataset = db.get_dataset(dataset)

        affiliation = self.get_argument("affiliation", strip=False)  # pylint: disable=no-value-for-parameter
        country = self.get_argument("country", strip=False)  # pylint: disable=no-value-for-parameter
        newsletter = self.get_argument("newsletter", strip=False)  # pylint: disable=no-value-for-parameter

        user.affiliation = affiliation
        user.country = country

        logging.info(f"Inserting into database: {user.name}, {user.email}")

        try:
            with db.database.atomic():
                user.save()  # Save to database
                ds_access, _ = db.DatasetAccess.get_or_create(user=user,
                                                              dataset=dataset)
                ds_access.wants_newsletter = newsletter
                ds_access.save()
                db.UserAccessLog.create(user=user,
                                        dataset=dataset,
                                        action='access_requested')
        except peewee.OperationalError as err:
            logging.error(f"Database Error: {err}")


class LogEvent(handlers.SafeHandler):
    def post(self, dataset, event, target):
        dataset, _ = utils.parse_dataset(dataset)
        user = self.current_user

        if event == 'consent':
            user.save()
            ds_version = (db.DatasetVersion
                          .select()
                          .join(db.Dataset)
                          .where(db.DatasetVersion.version == target,
                                 db.Dataset.short_name == dataset)
                          .get())
            db.UserConsentLog.create(user=user,
                                     dataset_version=ds_version)
        else:
            raise tornado.web.HTTPError(400, reason="Can't log that")


class ApproveUser(handlers.AdminHandler):
    def post(self, dataset, email):
        dataset, _ = utils.parse_dataset(dataset)
        with db.database.atomic():
            dataset = db.get_dataset(dataset)

            user = db.User.select().where(db.User.email == email).get()

            ds_access = (db.DatasetAccess.select()
                         .where(db.DatasetAccess.user == user,
                                db.DatasetAccess.dataset == dataset)
                         .get())
            ds_access.has_access = True
            ds_access.save()

            db.UserAccessLog.create(user=user,
                                    dataset=dataset,
                                    action='access_granted')

        try:
            msg = MIMEMultipart()
            msg['to'] = email
            msg['from'] = settings.from_address  # pylint: disable=no-member
            msg['subject'] = 'Swefreq access granted to {}'.format(dataset.short_name)
            msg.add_header('reply-to', settings.reply_to_address)  # pylint: disable=no-member
            body = """You now have access to the {} dataset

    Please visit https://swefreq.nbis.se/dataset/{}/download to download files.
            """.format(dataset.full_name, dataset.short_name)
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(settings.mail_server)  # pylint: disable=no-member
            server.sendmail(msg['from'], [msg['to']], msg.as_string())
        except smtplib.SMTPException as err:
            logging.error(f"Email error: {err}")
        except socket.gaierror as err:
            logging.error(f"Email error: {err}")

        self.finish()


class RevokeUser(handlers.AdminHandler):
    def post(self, dataset, email):  # pylint: disable=no-self-use
        dataset, _ = utils.parse_dataset(dataset)
        with db.database.atomic():
            dataset = db.get_dataset(dataset)
            user = db.User.select().where(db.User.email == email).get()

            db.UserAccessLog.create(user=user,
                                    dataset=dataset,
                                    action='access_revoked')


def _build_json_response(query, access_for):
    json_response = []
    for user in query:
        apply_date = '-'
        access = access_for(user)
        if not access:
            continue
        access = access[0]
        if access.access_requested:
            apply_date = access.access_requested.strftime('%Y-%m-%d')

        data = {'user': user.name,
                'email': user.email,
                'affiliation': user.affiliation,
                'country': user.country,
                'newsletter': access.wants_newsletter,
                'has_access': access.has_access,
                'applyDate': apply_date}
        json_response.append(data)
    return json_response


class DatasetUsersPending(handlers.AdminHandler):
    def get(self, dataset):
        dataset, _ = utils.parse_dataset(dataset)
        dataset = db.get_dataset(dataset)
        users = db.User.select()
        access = (db.DatasetAccessPending
                  .select()
                  .where(db.DatasetAccessPending.dataset == dataset))
        query = peewee.prefetch(users, access)

        self.finish({'data': _build_json_response(query, lambda u: u.access_pending)})


class DatasetUsersCurrent(handlers.AdminHandler):
    def get(self, dataset):
        dataset, _ = utils.parse_dataset(dataset)
        dataset = db.get_dataset(dataset)
        users = db.User.select()
        access = (db.DatasetAccessCurrent.select()
                  .where(db.DatasetAccessCurrent.dataset == dataset))
        query = peewee.prefetch(users, access)
        self.finish({'data': sorted(_build_json_response(
            query, lambda u: u.access_current), key=lambda u: u['applyDate'])})


class UserDatasetAccess(handlers.SafeHandler):
    def get(self):
        user = self.current_user

        ret = {"data": []}

        for access in user.access_pending:
            accessp_dict = {}
            accessp_dict['short_name'] = access.dataset.short_name
            accessp_dict['wants_newsletter'] = access.wants_newsletter
            accessp_dict['is_admin'] = False
            accessp_dict['access'] = False

            ret['data'].append(accessp_dict)

        for access in user.access_current:
            accessc_dict = {}
            accessc_dict['short_name'] = access.dataset.short_name
            accessc_dict['wants_newsletter'] = access.wants_newsletter
            accessc_dict['is_admin'] = access.is_admin
            accessc_dict['access'] = True

            ret['data'].append(accessc_dict)

        self.finish(ret)


class ServeLogo(handlers.UnsafeHandler):
    def get(self, dataset):
        dataset, _ = utils.parse_dataset(dataset)
        try:
            logo_entry = (db.DatasetLogo.select(db.DatasetLogo)
                          .join(db.Dataset)
                          .where(db.Dataset.short_name == dataset)
                          .get())
        except db.DatasetLogo.DoesNotExist:
            self.send_error(status_code=404)
            return

        self.set_header("Content-Type", logo_entry.mimetype)
        self.write(logo_entry.data.tobytes())
        self.finish()


class SFTPAccess(handlers.SafeHandler):
    """Creates, or re-enables, sFTP users in the database."""
    def get(self):
        """Returns sFTP credentials for the current user."""
        if db.get_admin_datasets(self.current_user).count() <= 0:
            self.finish({'user': None, 'expires': None, 'password': None})
            return

        password = None
        username = None
        expires = None
        # Check if an sFTP user exists for the current user
        try:
            data = self.current_user.sftp_user.get()
            username = data.user_name
            expires = data.account_expires.strftime("%Y-%m-%d %H:%M")
        except db.SFTPUser.DoesNotExist:
            # Otherwise return empty values
            pass

        self.finish({'user': username,
                     'expires': expires,
                     'password': password})

    def post(self):
        """
        Handles generation of new credentials. This function either creates a
        new set of sftp credentials for a user, or updates the old ones with a
        new password and expiry date.
        """
        if db.get_admin_datasets(self.current_user).count() <= 0:
            self.finish({'user': None, 'expires': None, 'password': None})
            return

        # Create a new password
        username = "_".join(self.current_user.name.split()) + "_sftp"
        password = self.generate_password()
        expires = datetime.today() + timedelta(days=30)

        # Check if an sFTP user exists for the current user when the database is ready
        passwd_hash = fn.encode(fn.digest(password, 'sha256'), 'hex')

        try:
            self.current_user.sftp_user.get()
            # if we have a user, update it
            (db.SFTPUser.update(password_hash=passwd_hash,
                                account_expires=expires)
             .where(db.SFTPUser.user == self.current_user)
             .execute())
        except db.SFTPUser.DoesNotExist:
            # if there is no user, insert the user in the database
            (db.SFTPUser.insert(user=self.current_user,    # pylint: disable=no-value-for-parameter
                                user_uid=db.get_next_free_uid(),
                                user_name=username,
                                password_hash=passwd_hash,
                                account_expires=expires).execute())

        self.finish({'user': username,
                     'expires': expires.strftime("%Y-%m-%d %H:%M"),
                     'password': password})

    def generate_password(self, size: int = 12) -> str:  # pylint: disable=no-self-use
        """
        Generates a password of length 'size', comprised of random lowercase and
        uppercase letters, and numbers.

        Args:
            size: The length of the password that will be generated

        Returns:
            str: The generated password

        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

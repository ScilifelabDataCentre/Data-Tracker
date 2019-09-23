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


class LogEvent(handlers.SafeHandler):
    def post(self, dataset, event, target):
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

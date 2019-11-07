import logging

import tornado.web
import tornado

import db
import handlers
import portal_errors
import portal_utils


class AddDataset(handlers.StewardHandler):
    """
    Add a new Dataset to the db.
    """
    def get(self):
        """The intended data structure for POST."""
        data = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'doi': 'DOI',
                            'creator': 'Creator',
                            'dmp': 'Data Management Plan',
                            'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                            'publications': [{'identifier': 'Publication'}],
                            'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                            'projects': ['project_id']}}

        self.finish(data)

    def post(self):
        """
        Add a dataset.

        Expects a JSON structure:
        ```
        {"dataset": {<dataset values>}}
        ```
        """
        data = tornado.escape.json_decode(self.request.body)

        if not 'dataset' in data or not 'projects' in data['dataset']:
            logging.debug(f'add dataset failed: {data}')
            logging.info('AddDataset: bad request (dataset)')
            self.send_error(status_code=400)
            return

        ds_data = data['dataset']
        if 'title' not in ds_data or not ds_data['title']:
            logging.info('AddDataset: bad request (title)')
            self.send_error(status_code=400)
            return

        ds_to_add = {header: ds_data[header]
                     for header in ('title',
                                    'description',
                                    'doi',
                                    'creator',
                                    'contact',
                                    'dmp',
                                    'visible')
                     if header in ds_data}

        with db.database.atomic():
            ds_id = db.Dataset.create(**ds_to_add)
            for project in ds_data['projects']:
                db.ProjectDataset.create(project=project,
                                         dataset=ds_id)

            for tag in ds_data['tags']:
                tag_id, _ = db.Tag.get_or_create(**tag)
                db.DatasetTag.create(dataset=ds_id,
                                     tag=tag_id)

            for publication in ds_data['publications']:
                pub_id, _ = db.Publication.get_or_create(**publication)
                db.DatasetPublication.create(dataset=ds_id,
                                             publication=pub_id)

            for data_url in ds_data['dataUrls']:
                url_id, _ = db.DataUrl.get_or_create(**data_url)
                db.DatasetDataUrl.create(dataset=ds_id,
                                         data_url=url_id)
        self.finish()


class CountryList(handlers.UnsafeHandler):
    """List countries."""
    def get(self):
        """
        Provide a JSON structure with country names:
        ```
        {"countries": [{"name": <country name>]}
        ```
        """
        self.write({'countries': [{'name': c} for c in self.country_list]})

    @property
    def country_list(self):
        return ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola",
                "Anguilla", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba",
                "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
                "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia",
                "Bosnia and Herzegovina", "Botswana", "Brazil", "British Indian Ocean Territory",
                "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
                "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands",
                "Central African Republic", "Chad", "Chile", "China", "Christmas Island",
                "Cocos Islands", "Colombia", "Comoros", "Cook Islands", "Costa Rica",
                "Croatia", "Cuba", "Curacao", "Cyprus", "Czech Republic",
                "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica",
                "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador",
                "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands",
                "Faroe Islands", "Fiji", "Finland", "France", "French Polynesia", "Gabon", "Gambia",
                "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada",
                "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
                "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq",
                "Ireland", "Isle of Man", "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan",
                "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait",
                "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
                "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Madagascar", "Malawi",
                "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania",
                "Mauritius", "Mayotte", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
                "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru",
                "Nepal", "Netherlands", "Netherlands Antilles", "New Caledonia", "New Zealand",
                "Nicaragua", "Niger", "Nigeria", "Niue", "North Korea", "North Macedonia",
                "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestine",
                "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn",
                "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of the Congo", "Reunion",
                "Romania", "Russia", "Rwanda", "Saint Barthelemy", "Saint Helena",
                "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin", "Saint Pierre and Miquelon",
                "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
                "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
                "Sint Maarten", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
                "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan",
                "Suriname", "Svalbard and Jan Mayen", "Swaziland", "Sweden", "Switzerland", "Syria",
                "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tokelau", "Tonga",
                "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
                "Turks and Caicos Islands", "Tuvalu", "U.S. Virgin Islands", "Uganda", "Ukraine",
                "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
                "Vanuatu", "Vatican", "Venezuela", "Vietnam", "Wallis and Futuna", "Western Sahara",
                "Yemen", "Zambia", "Zimbabwe"]


class DeleteDataset(handlers.StewardHandler):
    """Delete a dataset"""
    def get(self, ds_identifier: int = None):
        """
        Delete dataset or get data structure for POST.

        Args:
            ds_identifier (int): dataset identifier; if present the dataset will be deleted
        """
        if not ds_identifier:
            data = {'identifier': 9876543210}
        else:
            try:
                dataset = db.Dataset.get_by_id(ds_identifier)
            except db.Dataset.DoesNotExist:
                logging.info('Bad request (dataset does not exist)')
                self.send_error(status_code=400, reason="Dataset does not exist")
                return
            dataset.delete_instance()
            data = None
        self.finish(data)


    def post(self, ds_identifier: int = None):
        """
        Delete the dataset with the provided id.

        JSON structure:
        ```
        {"identifier": <ds_identifier> (int)}
        ```
        """
        if ds_identifier:
            data = {'identifier': ds_identifier}
        else:
            data = tornado.escape.json_decode(self.request.body)

        try:
            identifier = int(data['identifier'])
        except ValueError:
            logging.info('DeleteDataset: bad request (input not an integer)')
            self.send_error(status_code=400, reason="The identifier should be an integer")
            return
        try:
            dataset = db.Dataset.get_by_id(identifier)
        except db.Dataset.DoesNotExist:
            logging.info('AddDataset: bad request (dataset does not exist)')
            self.send_error(status_code=400, reason="Dataset does not exist")
            return
        dataset.delete_instance()

        self.finish()


class FindDataset(handlers.UnsafeHandler):
    """Find datasets matching a query"""
    def get(self):
        """Data structure for POST"""
        data = {'query': {'title': 'Title',
                          'creator': 'Creator',
                          'tags': ['Tag1'],
                          'publications': ['Title. Journal:Year']}}
        self.finish(data)

    def post(self):
        """
        Find datasets matching the query.

        Bad types will be ignored. No search will be performed if there are no valid terms.

        JSON structure:
        ```
        {"query": {"type": "value"}}
        ```
        """
        data = tornado.escape.json_decode(self.request.body)

        query = (db.Dataset
                 .select(db.Dataset.id)
                 .distinct())

        def search_publications(query, publications: list):
            query = (query.join(db.DatasetPublication)
                     .join(db.Publication)
                     .switch(db.Dataset))
            for publication in publications:
                query = query.where(db.Publication.identifier == publication)
            return query

        def search_tags(query, tags: list):
            query = (query.join(db.DatasetTag)
                     .join(db.Tag)
                     .switch(db.Dataset))
            for tag in tags:
                query = query.where(db.Tag.title == tag)
            return query

        search_functions = {'title': lambda q, t: q.where(db.Dataset.title.contains(t)),
                            'creator': lambda q, c: q.where(db.Dataset.creator.contains(c)),
                            'tags': search_tags,
                            'publications': search_publications}

        used = False
        for search_type in data['query']:
            if search_type in search_functions:
                used = True
                query = search_functions[search_type](query, data['query'][search_type])

        if not used:
            self.send_error(status_code=400)
            return

        # feels a bit bad, but is needed to get the complete dataset information
        datasets = [portal_utils.get_dataset(dataset.id, self.current_user) for dataset in query]

        self.finish({'datasets': datasets})


class GetDataset(handlers.UnsafeHandler):
    """Retrieve a dataset."""
    def get(self, ds_identifier: str):
        """
        Retrieve the wanted dataset.

        Args:
            ds_identifier (str): the database id of the wanted dataset

        """
        dbid = int(ds_identifier)
        try:
            dataset = portal_utils.get_dataset(dbid, self.current_user)
        except db.Dataset.DoesNotExist:
            logging.info('GetDataset: dataset does not exist')
            self.send_error(status_code=404)
            return
        except portal_errors.InsufficientPermissions:
            logging.info('GetDataset: insufficient permissions')
            self.send_error(status_code=403)
            return

        self.finish(dataset)


class GetCurrentUser(handlers.UnsafeHandler):
    """Retrieve basic information about the current user."""
    def get(self):
        user = self.current_user

        ret = {'user': None, 'email': None, 'permission': None}
        if user:
            ret = {'user': user.name,
                   'email': user.email,
                   'affiliation': user.affiliation,
                   'country': user.country,
                   'permission': user.permission}

        self.finish(ret)


class GetProject(handlers.UnsafeHandler):
    """Retrieve a dataset."""
    def get(self, project_id: str):
        """
        Retrieve the wanted dataset.

        Args:
            ds_identifier (str): the database id of the wanted dataset

        """
        dbid = int(project_id)
        try:
            dataset = portal_utils.get_project(dbid, self.current_user)
        except db.Dataset.DoesNotExist:
            logging.info('GetDataset: dataset does not exist')
            self.send_error(status_code=404)
            return
        except portal_errors.InsufficientPermissions:
            logging.info('GetDataset: insufficient permissions')
            self.send_error(status_code=403)
            return

        self.finish(dataset)


class ListDatasets(handlers.UnsafeHandler):
    def get(self):
        ret = list(db.Dataset
                   .select()
                   .dicts())

        self.finish({'datasets': ret})


class ListProjects(handlers.UnsafeHandler):
    def get(self):
        ret = list(db.Project
                   .select()
                   .dicts())

        self.finish({'projects': ret})


class ListUsers(handlers.AdminHandler):
    """Retrieve a list of all users, including permissions etc."""
    def get(self):
        users = list(db.User.select().dicts())
        self.finish({'users': users})


class UpdateDataset(handlers.SafeHandler):
    """Update the fields of a dataset."""
    def get(self, ds_identifier: str):
        """Data structure for POST."""
        data = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'doi': 'DOI',
                            'creator': 'Creator',
                            'dmp': 'Data Management Plan',
                            'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                            'publications': [{'identifier': 'Publication'}],
                            'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}]}}

        ds_id = int(ds_identifier)
        dataset = db.Dataset.get_by_id(ds_id)
        if not (portal_utils.has_rights(self.current_user, ('Steward', 'Admin'))
                or portal_utils.is_owner(self.current_user, dataset)):
            self.send_error(status_code=403)
            return

        self.finish(data)

    def post(self, ds_identifier: str):
        """
        Update the fields of a dataset.

        Args:
            ds_identifier (str): the id of a dataset, int(ds_id) must work

        """
        user = self.current_user
        ds_id = int(ds_identifier)

        try:
            dataset = db.Dataset.get_by_id(ds_id)
        except db.Dataset.DoesNotExist:
            logging.debug('Dataset not found')
            self.send_error(status_code=404, reason='Dataset not found')
            return

        if not (portal_utils.has_rights(user, ('Steward', 'Admin'))
                or portal_utils.is_owner(user, dataset)):
            logging.debug(f'Not permitted; user_id:{self.current_user.id}, ds_id:{ds_id}')
            self.send_error(status_code=403)
            return

        data = tornado.escape.json_decode(self.request.body)
        try:
            indata = data['dataset']
        except KeyError:
            logging.debug('"dataset" missing')
            self.send_error(status_code=400)
            return

        if 'owners' in indata and not portal_utils.has_rights(user, ('Steward', 'Admin')):
            self.send_error(status_code=403)
            return

        for header in indata:
            if header not in ('title',
                              'description',
                              'doi',
                              'creator',
                              'dmp',
                              'tags',
                              'publications',
                              'dataUrls',
                              'projects'):
                logging.debug('Bad header')
                logging.debug(indata)
                self.send_error(status_code=400)
                return

        status_code = self.update_db(dataset, indata)
        if status_code != 200:
            self.send_error(status_code=status_code)
            return

        self.finish()

    def update_db(self, dataset, indata: dict) -> int:  # pylint: disable=no-self-use,too-many-locals
        """
        Perform the database update.

        The method exists to make sure that atomic() does not cause trouble.

        Args:
            dataset: Dataset model
            indata (dict): The incoming dataset fields

        Returns:
            int: Recommended status_code

        """
        with db.database.atomic() as transaction:
            for header in ('title',
                           'description',
                           'doi',
                           'creator',
                           'dmp'):
                if header in indata:
                    setattr(dataset, header, indata[header])
            dataset.save()

            for value_type in ('tags', 'publications', 'dataUrls', 'owners'):
                if value_type not in indata:
                    continue
                val_dbname = value_type.capitalize().rstrip('s')
                val_sing = value_type.rstrip('s')
                if value_type == 'dataUrls':
                    val_dbname = 'DataUrl'
                    val_sing = 'data_url'
                elif value_type == 'projects':
                    val_dbname = 'User'
                    val_sing = 'user'

                val_db = getattr(db, val_dbname)
                if value_type == 'projects':
                    val_mapdb = getattr(db, 'ProjectDataset')
                else:
                    val_mapdb = getattr(db, 'Dataset' + val_dbname)

                old_vals = {tag.id for tag in (val_db.select(val_db)
                                               .join(val_mapdb)
                                               .where(val_mapdb.dataset == dataset.id))}

                new_vals = set()
                for value in indata[value_type]:
                    try:
                        val_id, _ = val_db.get_or_create(**value)
                    except TypeError as err:
                        logging.debug(err)
                        transaction.rollback()
                        return 400
                    except AttributeError as err:
                        logging.debug(err)
                        transaction.rollback()
                        return 400
                    new_vals.add(val_id)

                if old_vals != new_vals:
                    (val_mapdb
                     .delete()
                     .where(val_mapdb.dataset == dataset.id)
                     .execute())
                    (val_mapdb  # pylint: disable=no-value-for-parameter
                     .insert_many([{'dataset': dataset.id, val_sing: val} for val in new_vals])
                     .execute())
        return 200


class QuitHandler(handlers.UnsafeHandler):
    def get(self):  # pylint: disable=no-self-use
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.stop()

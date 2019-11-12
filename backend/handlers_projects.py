"""Project handlers."""

import logging

import tornado.web
import tornado

import db
import handlers
import portal_errors
import portal_utils


class AddProject(handlers.StewardHandler):
    """
    Add a new Project to the db.
    """
    def get(self):
        """The intended data structure for POST."""
        data = {'project': {'title': 'Title',
                            'description': 'Description',
                            'creator': 'Creator',
                            'datasets': []}}

        self.finish(data)

    def post(self):
        """
        Add a project.

        Expects a JSON structure:
        ```
        {"project": {<project values>}}
        ```
        """
        data = tornado.escape.json_decode(self.request.body)

        if not 'project' in data:
            logging.debug(f'add project failed: {data}')
            logging.info('AddProject: bad request (project)')
            self.send_error(status_code=400)
            return

        proj_data = data['project']
        if 'title' not in proj_data or not proj_data['title']:
            logging.info('AddProject: bad request (title)')
            self.send_error(status_code=400)
            return

        proj_to_add = {header: proj_data[header]
                       for header in ('title',
                                      'description',
                                      'creator')
                       if header in proj_data}

        with db.database.atomic():
            dbproject = db.Dataset.create(**proj_to_add)
            if 'datasets' in proj_data:
                for dataset_id in proj_data['datasets']:
                    db.ProjectDataset.create(project=dbproject,
                                             dataset=dataset_id)
        self.finish({'id': dbproject.id})


class GetProject(handlers.UnsafeHandler):
    """Retrieve a dataset."""
    def get(self, project_id: str):
        """
        Retrieve the wanted dataset.

        Args:
            project_id (str): the database id of the wanted dataset

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


class ListProjects(handlers.UnsafeHandler):
    def get(self):
        ret = list(db.Project
                   .select()
                   .dicts())

        self.finish({'projects': ret})


class UpdateProject(handlers.SafeHandler):
    """Update the fields of a project."""
    def get(self, project_id: str):
        """Data structure for POST."""
        data = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'contact': 'Contact',
                            'datasets': []
                            }}

        proj_id = int(project_id)
        project = db.Project.get_by_id(proj_id)

        if not (portal_utils.has_rights(self.current_user, ('Steward', 'Admin'))
                or portal_utils.is_owner(self.current_user, project, 'project')):
            self.send_error(status_code=403)
            return

        self.finish(data)

    def post(self, project_id: str):
        """
        Update the fields of a dataset.

        Args:
            project_id (str): the id of a dataset, int(proj_id) must work

        """
        proj_id = int(project_id)
        try:
            project = db.Project.get_by_id(proj_id)
        except db.Dataset.DoesNotExist:
            logging.debug('Project not found')
            self.send_error(status_code=404, reason='Project not found')
            return

        if not (portal_utils.has_rights(self.current_user, ('Steward', 'Admin'))
                or portal_utils.is_owner(self.current_user, project, 'project')):
            logging.debug(f'Not permitted; user_id:{self.current_user.id}, proj_id:{proj_id}')
            self.send_error(status_code=403)
            return

        data = tornado.escape.json_decode(self.request.body)
        try:
            indata = data['project']
        except KeyError:
            logging.debug('"project" missing')
            self.send_error(status_code=400)
            return

        for header in indata:
            if header not in ('id',
                              'title',
                              'description',
                              'contact',
                              'datasets'):
                logging.debug('Bad header')
                self.send_error(status_code=400)
                return

        status_code = self.update_db(project, indata)
        if status_code != 200:
            self.send_error(status_code=status_code)
            return

        self.finish()

    def update_db(self, project, indata: dict) -> int:  # pylint: disable=no-self-use,too-many-locals
        """
        Perform the database update.

        The method exists to make sure that atomic() does not cause trouble.

        Args:
            project: Project model
            indata (dict): The incoming project fields

        Returns:
            int: Recommended status_code

        """
        with db.database.atomic() as transaction:  # pylint: disable=unused-variable
            for header in ('title',
                           'description',
                           'contact'):
                if header in indata:
                    setattr(project, header, indata[header])
            project.save()
        return 200

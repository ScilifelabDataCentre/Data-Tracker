#!/usr/bin/env python3

from peewee import (BooleanField,
                    CompositeKey,
                    CharField,
                    Field,
                    ForeignKeyField,
                    Model,
                    TextField)
from playhouse.postgres_ext import PostgresqlExtDatabase

import settings

# pylint: disable=no-member
database = PostgresqlExtDatabase(settings.psql_name,
                                 user=settings.psql_user,
                                 password=settings.psql_pass,
                                 host=settings.psql_host,
                                 port=settings.psql_port,
                                 register_hstore=False)
# pylint: enable=no-member

class BaseModel(Model):
    class Meta:
        database = database


class EnumField(Field):
    db_field = 'string'  # The same as for CharField

    def __init__(self, choices=None, *args, **kwargs):
        self.values = choices or []
        super().__init__(*args, **kwargs)

    def db_value(self, value):
        if value not in self.values:
            raise ValueError("Illegal value for '{}'".format(self.column_name))
        return value

    def python_value(self, value):
        if value not in self.values:
            raise ValueError("Illegal value for '{}'".format(self.column_name))
        return value


class AuthKey(BaseModel):
    '''
    Auth keys for e.g. Order Portal.
    '''
    class Meta:
        table_name = 'auth_keys'
        schema = 'users'

    system_name = CharField(null=False)
    key_value = CharField(null=False)


class Dataset(BaseModel):
    '''
    A dataset.
    '''
    class Meta:
        table_name = 'datasets'
        schema = 'project_data'

    title = CharField(null=False)
    description = TextField(null=True)
    doi = CharField(null=True)
    creator = CharField(null=True)
    dmp = CharField(null=True)


class DataUrl(BaseModel):
    '''
    A url to obtain data for a dataset.
    '''
    class Meta:
        table_name = 'data_urls'
        schema = 'project_data'

    description = CharField()
    url = CharField()


class Project(BaseModel):
    '''
    A project.
    '''
    class Meta:
        table_name = 'projects'
        schema = 'project_data'

    title = CharField(null=False)
    description = TextField(null=True)
    contact = CharField(null=True)


class Publication(BaseModel):
    '''
    A publication for a dataset.
    '''
    class Meta:
        table_name = 'publications'
        schema = 'project_data'

    identifier = CharField()


class Tag(BaseModel):
    '''
    A tag for a dataset.
    '''
    class Meta:
        table_name = 'tags'
        schema = 'project_data'

    title = CharField()


class User(BaseModel):
    '''
    A user.
    '''
    class Meta:
        table_name = 'users'
        schema = 'users'

    name = CharField(column_name='given_name', null=True)
    email = CharField(unique=True)
    auth_identity = CharField(unique=True, null=True)
    affiliation = CharField(null=True)
    country = CharField(null=True)
    permission = EnumField(null=False,
                           choices=['Standard', 'Steward', 'Admin'],
                           default='Standard')


# Table mappings

class DatasetDataUrl(BaseModel):
    class Meta:
        table_name = 'dataset_data_url_map'
        schema = 'project_data'
        primary_key = CompositeKey('dataset', 'data_url')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id', on_delete='CASCADE')
    data_url = ForeignKeyField(DataUrl, column_name='data_url_id')


class DatasetPublication(BaseModel):
    class Meta:
        table_name = 'dataset_publication_map'
        schema = 'project_data'
        primary_key = CompositeKey('dataset', 'publication')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id', on_delete='CASCADE')
    publication = ForeignKeyField(Publication, column_name='publication_id')


class DatasetTag(BaseModel):
    class Meta:
        table_name = 'dataset_tag_map'
        schema = 'project_data'
        primary_key = CompositeKey('dataset', 'tag')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id', on_delete='CASCADE')
    tag = ForeignKeyField(Tag, column_name='tag_id', on_delete='CASCADE')


class ProjectDataset(BaseModel):
    class Meta:
        table_name = 'project_dataset_map'
        schema = 'project_data'
        primary_key = CompositeKey('project', 'dataset')

    project = ForeignKeyField(Project, column_name='project_id', on_delete='CASCADE')
    dataset = ForeignKeyField(Dataset, column_name='dataset_id', on_delete='CASCADE')


class ProjectOwner(BaseModel):
    """
    Project owners (users)
    """
    class Meta:
        table_name = 'project_owners'
        schema = 'users'
        primary_key = CompositeKey('project', 'user')

    project = ForeignKeyField(Project, column_name='project_id', on_delete='CASCADE')
    user = ForeignKeyField(User, column_name='user_id')


class UserAuthKey(BaseModel):
    class Meta:
        table_name = 'user_auth_key_map'
        schema = 'users'
        primary_key = CompositeKey('user', 'auth_key')

    user = ForeignKeyField(User, column_name='user_id', on_delete='CASCADE')
    auth_key = ForeignKeyField(AuthKey, column_name='auth_key_id', on_delete='CASCADE')


def build_dict_from_row(row) -> dict:
    """Build a dictionary from a row object"""
    outdict = {}

    for field, value in row.__dict__['__data__'].items():
        if field == "id":
            continue
        outdict[field] = value
    return outdict

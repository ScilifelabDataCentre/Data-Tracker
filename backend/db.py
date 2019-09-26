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


class Dataset(BaseModel):
    '''
    A dataset.
    '''
    class Meta:
        table_name = 'datasets'
        schema = 'datasets'

    title = CharField(null=False)
    description = TextField(null=True)
    doi = CharField(null=True)
    creator = CharField(null=True)
    contact = CharField(null=True)
    dmp = CharField(null=True)
    visible = BooleanField(null=False)


class DataUrl(BaseModel):
    '''
    A url to obtain data for a dataset.
    '''
    class Meta:
        table_name = 'data_urls'
        schema = 'datasets'

    description = CharField()
    url = CharField()


class Publication(BaseModel):
    '''
    A publication for a dataset.
    '''
    class Meta:
        table_name = 'publications'
        schema = 'datasets'

    identifier = CharField()


class Tag(BaseModel):
    '''
    A tag for a dataset.
    '''
    class Meta:
        table_name = 'tags'
        schema = 'datasets'

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
    auth_identity = CharField(unique=True)
    affiliation = CharField(null=True)
    country = CharField(null=True)
    permission = EnumField(null=False, choices=['Standard', 'Steward', 'Admin'])


# Table mappings

class DatasetDataUrl(BaseModel):
    class Meta:
        table_name = 'dataset_data_url_map'
        schema = 'datasets'
        primary_key = CompositeKey('dataset_id', 'data_url_id')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id')
    data_url = ForeignKeyField(DataUrl, column_name='data_url_id')


class DatasetPublication(BaseModel):
    class Meta:
        table_name = 'dataset_publication_map'
        schema = 'datasets'
        primary_key = CompositeKey('dataset_id', 'publication_id')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id')
    publication = ForeignKeyField(Publication, column_name='publication_id')


class DatasetTag(BaseModel):
    class Meta:
        table_name = 'dataset_tag_map'
        schema = 'datasets'
        primary_key = CompositeKey('dataset_id', 'tag_id')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id')
    tag = ForeignKeyField(Tag, column_name='tag_id')


class DatasetUser(BaseModel):
    class Meta:
        table_name = 'dataset_user_map'
        schema = 'users'
        primary_key = CompositeKey('dataset_id', 'user_id')

    dataset = ForeignKeyField(Dataset, column_name='dataset_id')
    user = ForeignKeyField(User, column_name='user_id')


def build_dict_from_row(row) -> dict:
    """Build a dictionary from a row object"""
    outdict = {}

    for field, value in row.__dict__['__data__'].items():
        if field == "id":
            continue
        outdict[field] = value
    return outdict

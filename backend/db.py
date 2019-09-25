#!/usr/bin/env python3

import logging

from peewee import (CompositeKey,
                    CharField,
                    DateTimeField,
                    IntegerField,
                    Field,
                    ForeignKeyField,
                    Model,
                    TextField,
                    fn)
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


class Dataset(BaseModel):
    '''
    A dataset.
    '''
    class Meta:
        table_name = 'datasets'
        schema = 'datasets'

    title = CharField()
    description = TextField(null=True)
    doi = CharField(null=True)
    creator = CharField(null=True)
    publication = CharField(null=True)
    contact = CharField(null=True)
    dmp = CharField(null=True)


class DataUrl(BaseModel):
    '''
    A url to obtain data for a dataset.
    '''
    class Meta:
        table_name = 'data_urls'
        schema = 'datasets'

    description = CharField()
    url = CharField()


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


# Table mappings

class DatasetTag(BaseModel):
    class Meta:
        table_name = 'dataset_tag_map'
        schema = 'dataset'
        primary_key = CompositeKey('dataset_id', 'tag_id')

    dataset_id = ForeignKeyField(Dataset)
    tag_id = ForeignKeyField(Tag)


class DatasetDataUrl(BaseModel):
    class Meta:
        table_name = 'dataset_tag_map'
        schema = 'dataset'
        primary_key = CompositeKey('dataset_id', 'data_url_id')

    dataset_id = ForeignKeyField(Dataset)
    data_url_id = ForeignKeyField(DataUrl)


class DatasetUser(BaseModel):
    class Meta:
        table_name = 'dataset_user_map'
        schema = 'users'
        primary_key = CompositeKey('dataset_id', 'user_id')

    dataset_id = ForeignKeyField(Dataset)
    user_id = ForeignKeyField(User)

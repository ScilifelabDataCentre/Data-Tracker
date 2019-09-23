#!/usr/bin/env python3

import logging

from peewee import (BlobField,
                    BooleanField,
                    CharField,
                    DateTimeField,
                    IntegerField,
                    Field,
                    FloatField,
                    ForeignKeyField,
                    Model,
                    TextField,
                    fn)
from playhouse.postgres_ext import ArrayField, BinaryJSONField, PostgresqlExtDatabase

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

###
# Reference Tables
##

class Dataset(BaseModel):
    """
    A dataset is part of a study, and usually include a certain population.

    Most studies only have a single dataset, but multiple are allowed.
    """
    class Meta:
        table_name = 'datasets'
        schema = 'data'

    study = ForeignKeyField(Study, column_name="study", backref='datasets')
    short_name = CharField()
    full_name = CharField()
    browser_uri = CharField(null=True)
    beacon_uri = CharField(null=True)
    description = TextField(column_name="beacon_description", null=True)
    avg_seq_depth = FloatField(null=True)
    seq_type = CharField(null=True)
    seq_tech = CharField(null=True)
    seq_center = CharField(null=True)
    dataset_size = IntegerField()

    def has_image(self):
        try:
            DatasetLogo.get(DatasetLogo.dataset == self)
            return True
        except DatasetLogo.DoesNotExist:
            return False


class User(BaseModel):
    class Meta:
        table_name = "users"
        schema = 'users'

    name = CharField(column_name="username", null=True)
    email = CharField(unique=True)
    identity = CharField(unique=True)
    identity_type = EnumField(null=False, choices=['google', 'elixir'], default='elixir')
    affiliation = CharField(null=True)
    country = CharField(null=True)

    def is_admin(self, dataset):
        return (DatasetAccess.select()
                .where(DatasetAccess.dataset == dataset,
                       DatasetAccess.user == self,
                       DatasetAccess.is_admin)
                .count())

    def has_access(self, dataset, ds_version=None):
        """
        Check whether user has permission to access a dataset.

        Args:
            dataset (Database): peewee Database object
            ds_version (str): the dataset version

        Returns:
            bool: allowed to access

        """
        dsv = get_dataset_version(dataset.short_name, ds_version)
        if not dsv:
            return False
        if dsv.file_access in ('REGISTERED', 'PUBLIC'):
            return True
        if dsv.file_access == 'PRIVATE':
            return False

        return (DatasetAccessCurrent.select()
                .where(DatasetAccessCurrent.dataset == dataset,
                       DatasetAccessCurrent.user == self)
                .count()) > 0

    def has_requested_access(self, dataset):
        return (DatasetAccessPending.select()
                .where(DatasetAccessPending.dataset == dataset,
                       DatasetAccessPending.user == self)
                .count())


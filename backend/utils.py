"""General helper functions."""

import logging
import uuid

import bson
import flask
import pymongo


def check_csrf_token():
    """Compare the csrf token from the request with the one in the session."""
    token = flask.request.form.get('_csrf_token')
    if not token or token != flask.session.get('_csrf_token'):
        logging.warning('Bad csrf token received')
        flask.abort(flask.Response(status=400))


def gen_csrf_token() -> str:
    """
    Genereate a csrf token.

    Returns:
        str: the csrf token

    """
    return uuid.uuid4().hex


def clean_mongo(response):
    """
    Clean up a mongo response by removing e.g. ObjectId (_id).

    Changes are done in-place.

    Args:
        response: a response from mongodb.find() or .find_one() (dict or list of dicts)

    """
    to_remove = ('_id',)
    if isinstance(response, list):
        for entry in response:
            for key in to_remove:
                if key in entry:
                    del entry[key]
    else:
        for key in to_remove:
            if key in response:
                del response[key]


def get_dbserver() -> pymongo.mongo_client.MongoClient:
    """
    Get the connection to the MongoDB database server.

    Returns:
        pymongo.mongo_client.MongoClient: the client connection

    """
    return pymongo.MongoClient(host=flask.current_app.config['mongo']['host'],
                               port=flask.current_app.config['mongo']['port'],
                               username=flask.current_app.config['mongo']['user'],
                               password=flask.current_app.config['mongo']['password'])


def get_db(dbserver: pymongo.mongo_client.MongoClient) -> pymongo.database.Database:
    """
    Get the connection to the MongoDB database.

    Args:
        dbserver: connection to the db

    Returns:
        pymongo.database.Database: the database connection

    """
    return dbserver[flask.current_app.config['mongo']['db']]


def to_mongo_uuid(uuid_str: str) -> bson.binary.Binary:
    """
    Convert str uuid to the Mongo representation of UUID.

    Args:
        uuid_str (str): the uuid to be converted

    Returns:
        bson.binary.Binary: the uuid in Mongo encoding

    """
    return uuid_convert_mongo(uuid.UUID(uuid_str))


def new_uuid() -> bson.binary.Binary:
    """
    Generate a uuid for a field in a MongoDB document.

    Returns:
        bson.binary.Binary: the new uuid in binary format

    """
    return uuid_convert_mongo(uuid.uuid4())


def uuid_convert_mongo(in_uuid: uuid.UUID) -> bson.binary.Binary:
    """
    Convert uuid.UUID to the Mongo representation of UUID.

    Args:
        in_uuid (uuid.UUID): the uuid to be converted

    Returns:
        bson.binary.Binary: the uuid in Mongo encoding

    """
    return bson.binary.Binary(in_uuid.bytes, 4)

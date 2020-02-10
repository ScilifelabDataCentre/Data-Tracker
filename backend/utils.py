"""General helper functions."""

from collections import abc
import datetime
import logging
import re
import uuid

import bson
import flask
import pymongo


# csrf
def check_csrf_token():
    """Compare the csrf token from the request (header) with the one in the cookie.session."""
    token = flask.request.headers.get('X-CSRFToken')
    if not token or (token != flask.request.cookies.get('_csrf_token')):
        logging.warning('Bad csrf token received')
        flask.abort(flask.Response(status=400))


def gen_csrf_token() -> str:
    """
    Genereate a csrf token.

    Returns:
        str: the csrf token

    """
    return uuid.uuid4().hex


# db input/output
def check_mongo_update(document: dict):
    """
    Make sure that some fields in a document are not changed during an update.

    Also make sure indata is not empty.

    Args:
        document (dict): received input to update a document

    """
    if not document:
        return False
    forbidden = ('_id')
    for field in forbidden:
        if field in document:
            return False
    return True


def get_dataset(identifier: str):
    """
    Query for a dataset from the database.

    Args:
        identifier (str): the uuid of the dataset

    Returns:
        dict: the dataset

    """
    try:
        mongo_uuid = str_to_uuid(identifier)
        result = flask.g.db['datasets'].find_one({'_id': mongo_uuid})
        if not result:
            return None
        result['projects'] = list(flask.g.db['projects']
                                  .find({'datasets': result['_id']},
                                        {'title': 1, '_id': 1}))
    except ValueError:
        return None
    return result


def get_project(identifier: str):
    """
    Query for a project from the database.

    Args:
        identifier (str): the uuid of the project

    Returns:
        dict: the project

    """
    try:
        mongo_uuid = str_to_uuid(identifier)
        result = flask.g.db['projects'].find_one({'_id': mongo_uuid})
        if not result:
            return None
    except ValueError:
        return None
    return result


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
    codec_options = bson.codec_options.CodecOptions(uuid_representation=bson.binary.STANDARD)
    return dbserver.get_database(flask.current_app.config['mongo']['db'],
                                 codec_options=(codec_options))


def new_uuid() -> uuid.UUID:
    """
    Generate a uuid for a field in a MongoDB document.

    Returns:
        uuid.UUID: the new uuid in binary format

    """
    return uuid.uuid4()


def str_to_uuid(uuid_str: str) -> uuid.UUID:
    """
    Convert str uuid to uuid.UUID.

    Args:
        uuid_str (str): the uuid to be converted

    Returns:
        uuid.UUID: the uuid

    """
    return uuid.UUID(uuid_str)


# misc
def convert_keys_to_camel(chunk):
    """
    Convert keys given in snake_case to camelCase.

    The capitalization of the first letter is preserved.

    Args:
        chunk: Object to convert

    Returns:
        *: chunk converted to camelCase dict, otherwise chunk

    """
    if isinstance(chunk, abc.Sequence) and not isinstance(chunk, str):
        return [convert_keys_to_camel(e) for e in chunk]

    if not isinstance(chunk, abc.Mapping):
        return chunk

    new_chunk = {}
    for key, value in chunk.items():
        if key == '_id':
            new_chunk[key] = value
            continue
        # First character should be the same as in the original string
        new_key = key[0] + "".join([a[0].upper() + a[1:] for a in key.split("_")])[1:]
        new_chunk[new_key] = convert_keys_to_camel(value)
    return new_chunk


def country_list():
    """
    Provide a list of countries.

    Returns:
        list: A selection of countries.
    """
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


REGEX = {'email': re.compile(r'.*@.*\..*')}


def is_email(indata: str):
    """
    Check whether a string seems to be an email address or not.

    Args:
        indata (str): data to check

    Returns:
        bool: is the indata an email address or not

    """
    return bool(REGEX['email'].search(indata))


def is_owner(dataset: str = None, project: str = None):
    """
    Check if the current user owns the given dataset or project.

    If both a dataset and a project is provided, an exception will be raised.

    Args:
        dataset (str): the dataset to check
        project (str): the project to check

    Returns:
        bool: whether the current owns the dataset/project

    Raises:
        ValueError: one of dataset or project must be set, and not both

    """
    if dataset and project:
        raise ValueError('Only one of dataset and project should be set')
    if dataset:
        try:
            muuid = str_to_uuid(dataset)
        except ValueError:
            flask.abort(flask.Response(status=401))
        projects = list(flask.g.db['projects'].find({'datasets': muuid},
                                                    {'owner': 1, 'datasets': 1, '_id': 0}))
        owners = [project['owner'] for project in projects]
    elif project:
        proj_data = get_project(project)
        if not proj_data:
            flask.abort(status=404)
        owners = [project['owner']]
    else:
        raise ValueError('Either dataset or project must be set')

    if flask.g.current_user['email'] in owners:
        return True
    return False


def response_json(json_structure: dict):
    """
    Convert keys to camelCase and run `flask.jsonify()`.

    Args:
        json_structure (dict): structure to prepare

    Returns:
        flask.Response: prepared response containing json structure with camelBack keys
    """
    data = convert_keys_to_camel(json_structure)
    return flask.jsonify(data)


def make_timestamp():
    """
    Generate a timestamp of the current time.

    returns:
        datetime.datetime: the current time
    """
    return datetime.datetime.now()


def make_log(data_type: str, action: str, data: dict = None):
    """
    Log a change in the system.

    Saves a complete copy of the new object.

    It is assumed that all values are curated,
    e.g. that data only contains permitted fields.

    ``
    {
        'action': ('add', 'edit', 'delete'),
        'data_type': type of data, e.g. 'order',
        'entry': the entry id (_id),
        'fields': {modified fields with the old data},
        'timestamp': the current time,
        'user': the id of the current user
    }
    ``

    Args:
        action (str): type of action (insert, update etc)
        data_type (str): the collection name
        data (dict): the new data for the entry

    """
    flask.g.db['logs'].insert_one({'action': action,
                                   'data_type': data_type,
                                   'data': data,
                                   'timestamp': make_timestamp(),
                                   'user': flask.g.current_user['_id']})

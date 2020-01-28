"""General helper functions."""

import datetime
import logging
import uuid

import bson
import flask
import pymongo


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


def clean_mongo(response):
    """
    Prepare for returning a MongoDB document by e.g. `ObjectId (_id)`.

    Actions:
    * Remove `_id`
    * convert snake_case to camelCase

    Changes are done in-place.

    Args:
        response: a response from `mongodb.find()` or `.find_one()` (dict or list of dicts)

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


def convert_keys_to_camel(chunk):
    """
    Convert keys given in snake_case to camelCase.

    The capitalization of the first letter is preserved.

    Args:
        chunk: Object to convert

    Returns:
        *: chunk converted to camelCase dict, otherwise chunk

    """
    if isinstance(chunk, list):
        return [convert_keys_to_camel(e) for e in chunk]

    if not isinstance(chunk, dict):
        return chunk

    new_chunk = {}
    for key, value in chunk.items():
        # First character should be the same as in the original string
        new_key = key[0] + "".join([a[0].upper() + a[1:] for a in key.split("_")])[1:]
        new_chunk[new_key] = convert_keys_to_camel(value)
    return new_chunk


def check_mongo_update(document: dict):
    """
    Make sure that some fields in a document are not changed during an update.

    Also make sure indata is not empty.

    Args:
        document (dict): received input to update a document

    """
    if not document:
        return False
    forbidden = ('_id', 'timestamp', 'uuid')
    for field in forbidden:
        if field in document:
            return False
    return True


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


def get_dataset(identifier: str):
    """
    Query for a dataset from the database.

    Args:
        identifier (str): the uuid of the dataset

    Returns:
        dict: the dataset

    """
    try:
        mongo_uuid = to_mongo_uuid(identifier)
        result = flask.g.db['datasets'].find_one({'uuid': mongo_uuid})
        if not result:
            return None
        result['projects'] = list(flask.g.db['projects']
                                  .find({'datasets': uuid_convert_mongo(result['uuid'])},
                                        {'title': 1, 'uuid': 1, '_id': 0}))
        clean_mongo(result)
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
        mongo_uuid = to_mongo_uuid(identifier)
        result = flask.g.db['projects'].find_one({'uuid': mongo_uuid})
        if not result:
            return None
        clean_mongo(result)
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
    return dbserver[flask.current_app.config['mongo']['db']]


def is_owner(dataset: str = None, project: str = None):
    """
    Check if the current user owns the given dataset or project.

    If both a dataset and a project is provided, an exception will be raised.

    Args:
        dataset (str): the dataset to check
        project (str: the project to check

    Returns:
        bool: whether the current owns the dataset/project

    Raises:
        ValueError: one of dataset or project must be set, and not both

    """
    if dataset and project:
        raise ValueError('Only one of dataset and project should be set')
    if dataset:
        try:
            mongo_uuid = to_mongo_uuid(dataset)
        except ValueError:
            flask.abort(flask.Response(status=401))
        projects = list(flask.g.db['projects'].find({'datasets': mongo_uuid},
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


def make_timestamp():
    """
    Generate a timestamp of the current time.

    returns:
        datetime.datetime: the current time
    """
    return datetime.datetime.now()


def make_log(data: dict, datatype: str, action: str):
    """
    Log a change in the system.

    Args:
        data (dict): the indata
        datatype (str): the collection
        action (str): type of action (insert, update etc)
    """
    return flask.g.db['logs'].insert_one({'data': data,
                                          'datatype': datatype,
                                          'action': action,
                                          'timestamp': make_timestamp(),
                                          'user': flask.g.current_user['email']})

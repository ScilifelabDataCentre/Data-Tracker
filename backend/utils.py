"""General helper functions."""

from collections import abc, namedtuple
from typing import Any, Union
import datetime
import html
import re
import secrets
import uuid

import argon2
import bson
import flask
import pymongo

import structure
import validate


ValidationResult = namedtuple("ValidationResult", ["result", "status"])


def basic_check_indata(
    indata: dict, reference_data: dict, prohibited: Union[tuple, list]
) -> tuple:
    """
    Perform basic checks of indata.

    * All fields are allowed in the entity type
    * If title is a field for the entity, it may not be empty
    * All fields are of the correct type
    * All prohibited fields are unchanged (if update)

    Args:
        indata (dict): The incoming data.
        reference_data (dict): Either the old data or a reference dict.
        prohibited (Union[tuple, list]): Fields that may not be modified.
            If they are included in ``indata``, their values must be equal to the
            values in ``reference_data``. Defaults to ``None``.

    Returns:
        namedtuple: (``bool``: whether the check passed, ``code``: Suggested http code)
    """
    if prohibited is None:
        prohibited = []

    if (
        "title" in reference_data
        and not reference_data["title"]
        and not indata.get("title")
    ):
        flask.current_app.logger.debug("Title empty")
        return ValidationResult(result=False, status=400)

    for key in indata:
        if key in prohibited and indata[key] != reference_data[key]:
            flask.current_app.logger.debug("Prohibited key (%s) with new value", key)
            return ValidationResult(result=False, status=403)
        if key not in reference_data:
            flask.current_app.logger.debug("Bad key (%s)", key)
            return ValidationResult(result=False, status=400)
        if indata[key] != reference_data[key] and not validate.validate_field(
            key, indata[key]
        ):
            return ValidationResult(result=False, status=400)
    return ValidationResult(result=True, status=200)


def secure_description(data: str):
    """
    Process the description to make sure it does not contain dangerous data.

    Current checks:
    * Escape HTML

    Args:
        data: The description to process.

    Returns:
        str: The processed description.
    """
    return html.escape(data)


# csrf
def verify_csrf_token(request: flask.request) -> bool:
    """
    Compare the csrf token from the request (header) with the one in ``cookie.session``.

    Args:
        request: The Flask request.

    Aborts with status 400 if the verification fails.
    """
    token = flask.request.headers.get("X-CSRFToken")
    if not token or (token != flask.request.cookies.get("_csrf_token")):
        flask.current_app.logger.warning("Bad csrf token received")
        flask.abort(status=400)


def gen_csrf_token() -> str:
    """
    Generate a csrf token.

    Returns:
        str: The csrf token.
    """
    return secrets.token_hex()


# API key
def gen_api_key():
    """
    Generate an API key with salt.

    Returns:
        APIkey: The API key with salt.
    """
    ApiKey = namedtuple("ApiKey", ["key", "salt"])
    return ApiKey(key=secrets.token_urlsafe(64), salt=secrets.token_hex(32))


def gen_api_key_hash(api_key: str, salt: str):
    """
    Generate a hash of the api_key for storing/comparing to db.

    Args:
        api_key (str): The cleartext API key (hex).
        salt (str): The salt to use (hex).

    Returns:
        str: SHA512 hash as hex.
    """
    ph = argon2.PasswordHasher()
    return ph.hash(api_key + salt)


def verify_api_key(username: str, api_key: str):
    """
    Verify an API key against the value in the database.

    Aborts with status 401 if the verification fails.

    Args:
        username (str): The username to check.
        api_key (str): The received API key (hex).
    """
    ph = argon2.PasswordHasher()
    user_info = flask.g.db["users"].find_one({"auth_ids": username})
    if not user_info:
        flask.current_app.logger.info("API key verification failed (bad username)")
        flask.abort(status=401)
    try:
        ph.verify(user_info["api_key"], api_key + user_info["api_salt"])
    except argon2.exceptions.VerifyMismatchError:
        flask.current_app.logger.info("API key verification failed (bad hash)")
        flask.abort(status=401)


def get_dbclient(conf) -> pymongo.mongo_client.MongoClient:
    """
    Get the connection to the MongoDB database server.

    Args:
        conf: A mapping with the relevant mongo keys available.

    Returns:
        pymongo.mongo_client.MongoClient: The client connection.
    """
    return pymongo.MongoClient(
        host=conf["mongo"]["host"],
        port=conf["mongo"]["port"],
        username=conf["mongo"]["user"],
        password=conf["mongo"]["password"],
    )


def get_db(
    dbserver: pymongo.mongo_client.MongoClient, conf
) -> pymongo.database.Database:
    """
    Get the connection to the MongoDB database.

    Args:
        dbserver (pymongo.mongo_client.MongoClient): Connection to the database.
        conf: A mapping with the relevant mongo keys available.

    Returns:
        pymongo.database.Database: The database connection.
    """
    codec_options = bson.codec_options.CodecOptions(
        uuid_representation=bson.binary.STANDARD
    )
    return dbserver.get_database(conf["mongo"]["db"], codec_options=(codec_options))


def new_uuid() -> uuid.UUID:
    """
    Generate a uuid for a field in a MongoDB document.

    Returns:
        uuid.UUID: The new uuid in binary format.
    """
    return uuid.uuid4()


def str_to_uuid(in_uuid: Union[str, uuid.UUID]) -> uuid.UUID:
    """
    Convert str uuid to uuid.UUID.

    Provided as a convenience function if the identifier must be changed in the future.

    Args:
        in_uuid (str or uuid.UUID): The uuid to be converted.

    Returns:
        uuid.UUID: The uuid as a UUID object.
    """
    if isinstance(in_uuid, str):
        return uuid.UUID(in_uuid)
    return in_uuid


# misc
def convert_keys_to_camel(chunk: Any) -> Any:
    """
    Convert keys given in snake_case to camelCase.

    The capitalization of the first letter is preserved.

    Args:
        chunk (Any): Object to convert.

    Returns:
        Any: Chunk converted to camelCase `dict`, otherwise chunk.
    """
    new_chunk = {}
    for key, value in chunk.items():
        if key == "_id":
            new_chunk[key] = value
            continue
        # First character should be the same as in the original string
        new_key = key[0] + "".join([a[0].upper() + a[1:] for a in key.split("_")])[1:]
        new_chunk[new_key] = convert_keys_to_camel(value)
    return new_chunk


REGEX = {"email": re.compile(r"[^@]+@[^@]+\.[^@]+")}


def is_email(indata: str):
    """
    Check whether a string seems to be an email address or not.

    Will not do thorough checking, just a basic check that the basic components are there.

    Args:
        indata (str): Data to check.

    Returns:
        bool: Is the indata an email address or not.
    """
    if not isinstance(indata, str):
        return False
    return bool(REGEX["email"].fullmatch(indata))


def response_json(data: dict):
    """
    Prepare a json response from the provided data.

    Args:
        date (dict): Structure to make into a respone.

    Returns:
        flask.Response: Prepared response containing json structure with camelBack keys.
    """
    url = flask.request.full_path
    return flask.jsonify(prepare_response(data, url))


def prepare_response(data: dict, url: str = ""):
    """
    Prepare the fields before running jsonify.

    ``data`` is modified in-place

    * Rename ``_id`` to ``id``
    * If available, add origin URL to the response

    Args:
        data (dict): Structure to prepare.

    Returns:
        dict:
    """
    if not isinstance(data, dict):
        return data

    def fix_id(chunk):
        """Recurse over the data structure to convert any ``_id`` to ``id``"""
        if not isinstance(chunk, dict):
            return chunk
        if "_id" in chunk:
            chunk["id"] = chunk["_id"]
            del chunk["_id"]
        for key, value in chunk.items():
            chunk[key] = fix_id(value)
        return chunk

    fix_id(data)
    if url:
        data["url"] = url

    return data


def make_timestamp():
    """
    Generate a timestamp of the current time.

    returns:
        datetime.datetime: The current time.
    """
    return datetime.datetime.now()


# pylint: disable=too-many-arguments
def make_log(
    data_type: str,
    action: str,
    comment: str,
    data: dict = None,
    no_user: bool = False,
    dbsession=None,
):
    """
    Log a change in the system.

    Saves a complete copy of the new object.

    Warning:
        It is assumed that all values are exactly like in the db,
        e.g. ``data`` should only contain permitted fields.

    Args:
        action (str): Type of action (add, edit, delete).
        comment (str): Note about why the change was done
            (e.g. "Dataset added via addDataset").
        data_type (str): The collection name.
        data (dict): The new data for the entry.
        no_user (bool): Whether the entry should be accredited to "system".
        dbsession: The MongoDB session used.

    Returns:
        bool: Whether the log insertion successed.
    """
    log = structure.log()
    if no_user:
        active_user = "system"
    else:
        active_user = flask.g.current_user["_id"]

    log.update(
        {
            "action": action,
            "comment": comment,
            "data_type": data_type,
            "data": data,
            "user": active_user,
        }
    )
    result = flask.g.db["logs"].insert_one(log, session=dbsession)
    if not result.acknowledged:
        flask.current_app.logger.error(
            f"Log failed: A:{action} C:{comment} D:{data} "
            + f'DT: {data_type} U: {flask.g.current_user["_id"]}'
        )
    return result.acknowledged


def incremental_logs(logs: list):
    """
    Make an incremental log.

    The log starts from the first log and keeps only
    the changed fields in ``data``.

    ``logs`` is changed in-place.
    """
    logs.sort(key=lambda x: x["timestamp"])
    for i in range(len(logs) - 1, 0, -1):
        del_keys = []
        for key in logs[i]["data"]:
            if logs[i]["data"][key] == logs[i - 1]["data"][key]:
                del_keys.append(key)
        for key in del_keys:
            del logs[i]["data"][key]


def check_email_uuid(user_identifier: str) -> Union[str, uuid.UUID]:
    """
    Check if the provided user is found in the db as email or _id.

    If the user is found, return the user.UUID of the user.
    If the identifier is a uuid, return a user.UUID.
    If the identifier is an email, return the email.

    Notes:
       ``user_identifier`` is assumed to be either a valid email or a valid uuid.

    Args:
        user_identifier (str): The identifier to look up.

    Returns:
        Union[str, uuid.UUID]: The new value for the field.
    """
    if is_email(user_identifier):
        user_entry = flask.g.db["users"].find_one({"email": user_identifier})
        if user_entry:
            return user_entry["_id"]
        return user_identifier
    try:
        user_uuid = str_to_uuid(user_identifier)
    except ValueError:
        return ""
    user_entry = flask.g.db["users"].find_one({"_id": user_uuid})
    if user_entry:
        return user_entry["_id"]
    return ""


def user_uuid_data(
    user_ids: Union[str, list, uuid.UUID], mongodb: pymongo.database.Database
) -> list:
    """
    Retrieve some extra information about a user using a uuid as input.

    Note that ``_id``` will be returned as ``str``, not ``uuid.UUID``.

    Args:
        user_ids (str, list, or uuid.UUID): UUID of the user(s).
        mongodb (pymongo.database.Database): The Mongo database to use for the query.

    Returns:
        list: The matching entries.
    """
    if isinstance(user_ids, str):
        user_uuids = [str_to_uuid(user_ids)]
    elif isinstance(user_ids, list):
        user_uuids = [str_to_uuid(entry) for entry in user_ids]
    else:
        user_uuids = [user_ids]
    data = mongodb["users"].find({"_id": {"$in": user_uuids}})
    return [
        {
            "_id": str(entry["_id"]),
            "affiliation": entry["affiliation"],
            "name": entry["name"],
            "contact": entry["contact"],
            "url": entry["url"],
            "orcid": entry["orcid"],
        }
        for entry in data
    ]

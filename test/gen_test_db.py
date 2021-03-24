#!/usr/bin/env python3
"""
Generate a test dataset.
"""
import random
import re
import string
import uuid

import bson
import lorem
import pymongo

import config
import structure
import utils
from user import PERMISSIONS


# helper functions
def make_description():
    """
    Make a random description based on lorem ipsum.

    Returns:
       str: a random description

    """
    desc = random.choice((lorem.sentence, lorem.paragraph, lorem.text))()
    desc = "# Title\n" + "\n## Subtitle\n\n".join(desc.split("\n\n"))
    return desc


def make_log(db, action, comment, data_type, data, user):
    log = structure.log()
    log.update(
        {
            "action": action,
            "comment": comment,
            "data_type": data_type,
            "data": data,
            "user": user,
        }
    )
    db["logs"].insert_one(log)


# generator functions
EXTRA_FIELDS = {
    "method": ("rna-seq", "chip-seq", "X-ray"),
    "external": ("company1", "company2", "company3"),
}
EXTRA_KEYS = tuple(EXTRA_FIELDS.keys())
EXTRA_VALUES = tuple(EXTRA_FIELDS.values())
EXTRA_VALUES = EXTRA_VALUES[0] + EXTRA_VALUES[1]


def gen_datasets(db, nr_datasets: int = 500):
    uuids = []
    orders = [entry["_id"] for entry in db["orders"].find()]
    for i in range(1, nr_datasets + 1):
        dataset = structure.dataset()
        changes = {"title": f"Dataset {i} Title", "description": make_description()}
        # add extra field
        if random.random() > 0.4:
            key = random.choice(EXTRA_KEYS)
            changes["properties"] = {key: random.choice(EXTRA_FIELDS[key])}
            changes["tags"] = list(
                set(random.choice(EXTRA_VALUES) for _ in range(random.randint(0, 6)))
            )
        dataset.update(changes)
        uuids.append(db["datasets"].insert_one(dataset).inserted_id)
        make_log(
            db,
            action="add",
            data=dataset,
            data_type="dataset",
            comment="Generated",
            user="system",
        )
        order_uuid = random.choice(orders)
        db["orders"].update_one({"_id": order_uuid}, {"$push": {"datasets": uuids[-1]}})
        order = db["orders"].find_one({"_id": order_uuid})
        make_log(
            db,
            action="edit",
            data=order,
            data_type="order",
            comment="Generated - add ds",
            user="system",
        )

    return uuids


def gen_facilities(db, nr_facilities: int = 30):
    uuids = []
    for i in range(1, nr_facilities + 1):
        user = structure.user()
        apikey = utils.gen_api_key()
        changes = {
            "affiliation": "University " + random.choice(string.ascii_uppercase),
            "api_key": utils.gen_api_key_hash(apikey.key, apikey.salt),
            "api_salt": apikey.salt,
            "auth_ids": [f"facility{i}::local"],
            "email": f"facility{i}@domain{i}.se",
            "contact": f"pub_facility{i}@domain{i}.se",
            "name": f"Facility {i}",
            "permissions": ["ORDERS"],
            "url": f"https://www.example.com/facility{i}",
        }
        user.update(changes)
        uuids.append(db["users"].insert_one(user).inserted_id)
        make_log(
            db,
            action="add",
            data=user,
            data_type="user",
            comment="Generated",
            user="system",
        )
    return uuids


def gen_organisations(db, nr_organisations: int = 15):
    uuids = []
    for i in range(1, nr_organisations + 1):
        user = structure.user()
        apikey = utils.gen_api_key()
        changes = {
            "affiliation": "Org/Uni " + random.choice(string.ascii_uppercase),
            "api_key": utils.gen_api_key_hash(apikey.key, apikey.salt),
            "api_salt": apikey.salt,
            "auth_ids": [f"organisation{i}::local"],
            "email": f"organisation{i}@domain{i}.se",
            "contact": f"pub_organisation{i}@domain{i}.se",
            "name": f"Organisation {i}",
            "permissions": ["ORDERS"],
            "url": f"https://www.example.com/org{i}",
        }
        user.update(changes)
        uuids.append(db["users"].insert_one(user).inserted_id)
        make_log(
            db,
            action="add",
            data=user,
            data_type="user",
            comment="Generated",
            user="system",
        )
    return uuids


def gen_orders(db, nr_orders: int = 300):
    uuids = []
    facility_re = re.compile("facility[0-9]*::local")
    organisation_re = re.compile("organisation[0-9]*::local")
    user_re = re.compile(".*::local")
    facilities = tuple(db["users"].find({"auth_ids": facility_re}))
    organisations = tuple(db["users"].find({"auth_ids": organisation_re}))
    users = tuple(
        db["users"].find({"$and": [{"auth_ids": user_re}, {"permissions": "ORDERS"}]})
    )
    for i in range(1, nr_orders + 1):
        order = structure.order()
        changes = {
            "authors": [
                random.choice(users)["_id"] for _ in range(random.randint(0, 4))
            ],
            "generators": [
                random.choice(facilities)["_id"] for _ in range(random.randint(0, 4))
            ],
            "organisation": random.choice(organisations)["_id"],
            "editors": [
                random.choice(users + facilities)["_id"]
                for _ in range(random.randint(1, 5))
            ],
            "description": make_description(),
            "title": f"Order {i} Title {lorem.sentence()[:-1]}",
        }
        if random.random() > 0.4:
            key = random.choice(EXTRA_KEYS)
            changes["properties"] = {key: random.choice(EXTRA_FIELDS[key])}
            changes["tags"] = list(
                set(random.choice(EXTRA_VALUES) for _ in range(random.randint(0, 6)))
            )
        order.update(changes)
        uuids.append(db["orders"].insert_one(order).inserted_id)
        make_log(
            db,
            action="add",
            data=order,
            data_type="order",
            comment="Generated",
            user="system",
        )
    return uuids


def gen_collections(db, nr_collections: int = 300):
    datasets = tuple(db["datasets"].find())
    users = tuple(db["users"].find({"affiliation": {"$ne": "Test University"}}))
    for i in range(1, nr_collections + 1):
        collection = structure.collection()
        changes = {
            "description": make_description(),
            "datasets": [
                random.choice(datasets)["_id"] for _ in range(random.randint(0, 5))
            ],
            "editors": list(
                set(random.choice(users)["_id"] for _ in range(random.randint(1, 3)))
            ),
            "title": f"Collection {i} Title",
        }
        if random.random() > 0.4:
            key = random.choice(EXTRA_KEYS)
            changes["properties"] = {key: random.choice(EXTRA_FIELDS[key])}
            changes["tags"] = list(
                set(random.choice(EXTRA_VALUES) for _ in range(random.randint(0, 6)))
            )
        collection.update(changes)
        db["collections"].insert_one(collection)
        make_log(
            db,
            action="add",
            data=collection,
            data_type="collection",
            comment="Generated",
            user="system",
        )


def gen_users(db, nr_users: int = 100):
    uuids = []
    perm_keys = tuple(PERMISSIONS.keys())
    # non-random users with specific rights
    special_users = [
        {"name": "Base", "permissions": []},
        {"name": "Orders", "permissions": ["ORDERS"]},
        {"name": "Owners", "permissions": ["OWNERS_READ"]},
        {"name": "Users", "permissions": ["USER_MANAGEMENT"]},
        {"name": "Data", "permissions": ["DATA_MANAGEMENT"]},
        {"name": "Root", "permissions": list(perm_keys)},
    ]
    for i, suser in enumerate(special_users):
        user = structure.user()
        user.update(suser)
        apikey = {"salt": "abc", "key": str(i)}
        user.update(
            {
                "affiliation": "Test University",
                "api_key": utils.gen_api_key_hash(apikey["key"], apikey["salt"]),
                "api_salt": apikey["salt"],
                "email": f'{"".join(user["name"].split())}@example.com',
                "contact": f'pub_{"".join(user["name"].split())}@example.com',
                "orcid": f"1111-1111-1111-111{i}",
                "auth_ids": [f'{user["name"].lower()}::testers'],
                "url": "https://www.example.com/specuser",
            }
        )
        db["users"].insert_one(user)
        make_log(
            db,
            action="add",
            data=user,
            data_type="user",
            comment="Generated",
            user="system",
        )

    for i in range(1, nr_users + 1):
        user = structure.user()
        apikey = utils.gen_api_key()
        changes = {
            "affiliation": "University " + random.choice(string.ascii_uppercase),
            "api_key": utils.gen_api_key_hash(apikey.key, apikey.salt),
            "api_salt": apikey.salt,
            "auth_ids": [f"user{i}::local"],
            "email": f"user{i}@place{i}.se",
            "contact": f"pub_user{i}@place{i}.se",
            "orcid": "-".join(f"{random.randint(0,10000):04}" for _ in range(4)),
            "name": f"First Last {i}",
            "permissions": list(
                set(random.choice(perm_keys) for _ in range(random.randint(0, 2)))
            ),
            "url": f"https://www.example.com/user{i}",
        }
        user.update(changes)
        uuids.append(db["users"].insert_one(user).inserted_id)
        make_log(
            db,
            action="add",
            data=user,
            data_type="user",
            comment="Generated",
            user="system",
        )
    return uuids


if __name__ == "__main__":
    CONF = config.read_config()
    DBSERVER = pymongo.MongoClient(
        host=CONF["mongo"]["host"],
        port=CONF["mongo"]["port"],
        username=CONF["mongo"]["user"],
        password=CONF["mongo"]["password"],
    )
    codec_options = bson.codec_options.CodecOptions(
        uuid_representation=bson.binary.STANDARD
    )
    DB = DBSERVER.get_database(CONF["mongo"]["db"], codec_options=(codec_options))
    gen_facilities(DB)
    gen_organisations(DB)
    gen_users(DB)
    gen_orders(DB)
    gen_datasets(DB)
    gen_collections(DB)

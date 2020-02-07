#!/usr/bin/env python3
"""
Generate a test dataset.
"""

import random
import string
import uuid

import lorem
import pymongo

import config
import structure
import utils


# helper functions
def make_description():
    """
    Make a random description based on lorem ipsum.

    Returns:
       str: a random description

    """
    desc = random.choice((lorem.sentence,
                          lorem.paragraph,
                          lorem.text))()
    desc.replace('\n', '<br/>')
    return desc


# generator functions
def gen_datasets(db, nr_datasets: int = 500):
    uuids = []
    orders = [utils.uuid_to_mongo_uuid(entry['_id']) for entry in db['orders'].find()]
    for i in range(1, nr_datasets+1):
        dataset = structure.dataset()
        changes = {'title': f'Dataset {i} Title',
                   'description': make_description(),
                   'links': [{'description': f'Download location {j}',
                                  'url': (f'https://data_source{i}/' +
                                          f'{random.choice(string.ascii_uppercase)}')}
                                 for j in range(1, random.randint(0, 6))]}
        dataset.update(changes)
        uuids.append(db['datasets'].insert_one(dataset).inserted_id)
        db['orders'].update_one({'_id': random.choice(orders)},
                                {'$push': {'datasets': uuids[-1]}})

    return uuids


def gen_facilities(db, nr_facilities: int = 30):
    countries = utils.country_list()
    uuids = []
    for i in range(1, nr_facilities+1):
        user = structure.user()
        changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
                   'name': f'Facility {i}',
                   'email': f'-facility-{i}',
                   'country': random.choice(countries),
                   'auth_id': uuid.uuid4().hex}
        user.update(changes)
        uuids.append(db['users'].insert_one(user).inserted_id)

    return uuids


def gen_orders(db, nr_orders: int = 300):
    uuids = []
    facilities = tuple(db['users'].find({'email': {'$regex': '^-facility-.*'}}))
    users = tuple(db['users'].find({'email': {'$regex': '.*@.*'}}))
    for i in range(1, nr_orders+1):
        order = structure.order()
        changes = {'title': f'Order {i} Title',
                   'description': make_description(),
                   'receiver': random.choice(users)['email'],
                   'creator': random.choice(facilities)['email']}

        order.update(changes)
        uuids.append(db['orders'].insert_one(order).inserted_id)
    return uuids


def gen_projects(db, nr_projects: int = 500):
    datasets = tuple(db['datasets'].find())
    users = tuple(db['users'].find())
    for i in range(1, nr_projects+1):
        project = structure.project()
        changes = {'title': f'Project {i} Title',
                   'description': make_description(),
                   'owner': random.choice(users)['email'],
                   'contact': f'email{i}@entity{i}',
                   'datasets': [utils.uuid_to_mongo_uuid(random.choice(datasets)['_id'])
                                for _ in range(random.randint(0, 5))],
                   'dmp': f'http://dmp-url{i}',
                   'publications': [f'Title {i}. Journal: 200{j}'
                                    for j in range(random.randint(0, 5))]}

        project.update(changes)
        db['projects'].insert_one(project)


def gen_users(db, nr_users: int = 100):
    uuids = []
    role_users = [{'name' : 'User Test', 'role' : 'User', 'email' : 'user@example.com',
                   'country' : 'Sweden', 'affiliation' : 'Test university', 'auth_id' : 'hash3@roles'},
                  {'name' : 'Steward Test', 'role' : 'Steward', 'email' : 'steward@example.com',
                   'country' : 'Sweden', 'affiliation' : 'Test university', 'auth_id' : 'hash2@roles'},
                  {'name' : 'Admin Test', 'role' : 'Admin', 'email' : 'admin@example.com',
                   'country' : 'Sweden', 'affiliation' : 'Test university', 'auth_id' : 'hash1@roles'}]

    base = [structure.user() for _ in range(3)]
    for i, entry in enumerate(base):
        entry.update(role_users[i])
    db['users'].insert_many(base)
    countries = utils.country_list()
    for i in range(1, nr_users+1-3):
        user = structure.user()
        changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
                   'name': f'First Last {i}',
                   'email': f'user{i}@place{i}',
                   'country': random.choice(countries),
                   'auth_id': f'hash{i}@elixir'}
        user.update(changes)
        uuids.append(db['users'].insert_one(user).inserted_id)
    return uuids


if __name__ == '__main__':
    CONF = config.read_config()
    DBSERVER = pymongo.MongoClient(host=CONF['mongo']['host'],
                                   port=CONF['mongo']['port'],
                                   username=CONF['mongo']['user'],
                                   password=CONF['mongo']['password'])
    DB = DBSERVER[CONF['mongo']['db']]
    gen_facilities(DB)
    gen_users(DB)
    gen_orders(DB)
    gen_datasets(DB)
    gen_projects(DB)

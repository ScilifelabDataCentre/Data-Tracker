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
    desc = random.choice((lorem.sentence,
                          lorem.paragraph,
                          lorem.text))()
    return desc


def make_log(db, action, comment, data_type, data, user):
    log = structure.log()
    log.update({'action': action,
                'comment': comment,
                'data_type': data_type,
                'data': data,
                'user': user})
    db['logs'].insert_one(log)


# generator functions
EXTRA_FIELDS = {'method': ('rna-seq', 'chip-seq', 'X-ray'),
                'external': ('company1', 'company2', 'company3')}
EXTRA_KEYS = tuple(EXTRA_FIELDS.keys())

def gen_datasets(db, nr_datasets: int = 500):
    uuids = []
    orders = [entry['_id'] for entry in db['orders'].find()]
    for i in range(1, nr_datasets+1):
        dataset = structure.dataset()
        changes = {'title': f'Dataset {i} Title',
                   'description': make_description(),
                   'links': [{'description': f'Download location {j}',
                              'url': (f'https://data_source{i}/' +
                                      f'{random.choice(string.ascii_uppercase)}')}
                                 for j in range(1, random.randint(0, 6))]}
        # add extra field
        if random.random() > 0.9:
            tag = random.choice(EXTRA_KEYS)
            changes['extra'] = [{tag: random.choice(EXTRA_FIELDS[tag])}]
        dataset.update(changes)
        uuids.append(db['datasets'].insert_one(dataset).inserted_id)
        make_log(db, action='add', data=dataset, data_type='dataset',comment='Generated', user='root')
        order_uuid = random.choice(orders)
        db['orders'].update_one({'_id': order_uuid},
                                {'$push': {'datasets': uuids[-1]}})
        order = db['orders'].find_one({'_id': order_uuid})
        make_log(db, action='update', data=order, data_type='order',comment='Generated - add ds', user='root')

    return uuids


def gen_facilities(db, nr_facilities: int = 30):
    uuids = []
    for i in range(1, nr_facilities+1):
        user = structure.user()
        apikey = utils.gen_api_key()
        changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
                   'api_key': utils.gen_api_key_hash(apikey.key, apikey.salt),
                   'api_salt': apikey.salt,
                   'auth_id': f'--facility {i}--',
                   'email': f'facility{i}@domain{i}',
                   'name': f'Facility {i}',
                   'permissions': ['ORDERS_SELF']}
        user.update(changes)
        uuids.append(db['users'].insert_one(user).inserted_id)
        make_log(db, action='add', data=user, data_type='user',comment='Generated', user='root')
    return uuids


def gen_orders(db, nr_orders: int = 300):
    uuids = []
    facility_re = re.compile('--facility [0-9]*--')
    facilities = tuple(db['users'].find({'auth_id': facility_re}))
    users = tuple(db['users'].find({'$and': [{'auth_id': {'$not': facility_re}},
                                             {'affiliation': {'$ne': 'Test University'}}]}))
    for i in range(1, nr_orders+1):
        receiver_type = random.choice(('email', '_id'))
        order = structure.order()
        changes = {'creator': random.choice(facilities)['_id'],
                   'description': make_description(),
                   'receiver': random.choice(users)[receiver_type],
                   'title': f'Order {i} Title'}
        order.update(changes)
        uuids.append(db['orders'].insert_one(order).inserted_id)
        make_log(db, action='add', data=order, data_type='order',comment='Generated', user='root')
    return uuids


def gen_projects(db, nr_projects: int = 500):
    datasets = tuple(db['datasets'].find())
    users = tuple(db['users'].find({'affiliation': {'$ne': 'Test University'}}))
    for i in range(1, nr_projects+1):
        project = structure.project()
        changes = {'contact': f'email{i}@entity{i}',
                   'description': make_description(),
                   'datasets': [random.choice(datasets)['_id']
                                for _ in range(random.randint(0, 5))],
                   'dmp': f'http://dmp-url{i}',
                   'owners': list(set(random.choice(users)[random.choice(('email', '_id'))]
                                      for _ in range(random.randint(1,3)))),
                   'publications': [{'title': f'Title {j}', 'doi': f'doi{j}'}
                                    for j in range(random.randint(0, 5))],
                   'title': f'Project {i} Title'}
        project.update(changes)
        db['projects'].insert_one(project)
        make_log(db, action='add', data=project, data_type='project',comment='Generated', user='root')


def gen_users(db, nr_users: int = 100):
    uuids = []
    perm_keys = tuple(PERMISSIONS.keys())
    # non-random users with specific rights
    special_users = [{'name': 'Base Test', 'permissions': [], 'auth_id' : 'base@testers'},
                     {'name': 'Orders Test', 'permissions': ['ORDERS_SELF'], 'auth_id' : 'orders@testers'},
                     {'name': 'Owners Test', 'permissions': ['OWNERS_READ'], 'auth_id' : 'owners@testers'},
                     {'name': 'Users Test', 'permissions': ['USER_MANAGEMENT'], 'auth_id' : 'users@testers'},
                     {'name': 'Data Test', 'permissions': ['DATA_MANAGEMENT'], 'auth_id' : 'data@testers'},
                     {'name': 'Doi Test', 'permissions': ['DOI_REVIEWER'], 'auth_id' : 'doi@testers'},
                     {'name': 'Root Test', 'permissions': list(perm_keys), 'auth_id' : 'root@testers'}]

    for i, suser in enumerate(special_users):
        user = structure.user()
        user.update(suser)
        user.update({'affiliation' : 'Test University',
                     'api_key': uuid.uuid4().hex,
                     'email': f'{"".join(user["name"].split())}@example.com'})
        db['users'].insert_one(user)
        make_log(db, action='add', data=user, data_type='user',comment='Generated', user='root')

    for i in range(1, nr_users+1):
        user = structure.user()
        apikey = utils.gen_api_key()
        changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
                   'api_key': utils.gen_api_key_hash(apikey.key, apikey.salt),
                   'api_salt': apikey.salt,
                   'auth_id': f'hash{i}@elixir',
                   'email': f'user{i}@place{i}',
                   'name': f'First Last {i}',
                   'permissions': list(set(random.choice(perm_keys)
                                           for _ in range(random.randint(0,2))))}
        user.update(changes)
        uuids.append(db['users'].insert_one(user).inserted_id)
        make_log(db, action='add', data=user, data_type='user',comment='Generated', user='root')
    return uuids


if __name__ == '__main__':
    CONF = config.read_config()
    DBSERVER = pymongo.MongoClient(host=CONF['mongo']['host'],
                                   port=CONF['mongo']['port'],
                                   username=CONF['mongo']['user'],
                                   password=CONF['mongo']['password'])
    codec_options = bson.codec_options.CodecOptions(uuid_representation=bson.binary.STANDARD)
    DB = DBSERVER.get_database(CONF['mongo']['db'],
                               codec_options=(codec_options))
    gen_facilities(DB)
    gen_users(DB)
    gen_orders(DB)
    gen_datasets(DB)
    gen_projects(DB)
    root_user = DB['users'].find_one({'name': 'Root Test'})
    DB['logs'].update_many({}, {'$set': {'user': root_user['_id']}})

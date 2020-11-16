"""DB initialisation and migration check."""
import logging
import sys

from migrations import MIGRATIONS
import utils
import structure

DB_VERSION = 1

def check_db(config: dict):
    """
    Perform database checks.

    - check if first-time setup has been performed
    - check that the data structure is up to date (migrations)

    Args:
        config (dict): Configuration for the data tracker
    """
    db = utils.get_db(utils.get_dbclient(config), config)
    db_initialised = db['db_status'].find_one({'_id': 'init_db'})
    if not db_initialised:
        init_db(db)
    else:
        check_migrations(db)


def init_db(db):
    """
    Do first time-setup for the database.

    - create a default user
    - set current db_version
    """
    db['db_status'].insert_one({'_id': 'init_db',
                                'started': True,
                                'user_added': False,
                                'finished': False})
    add_default_user(db)

    # Set DB version
    db['db_status'].insert_one({'_id': 'db_version',
                                'version': DB_VERSION})
    db['db_status'].update_one({'_id': 'init_db'},
                               {'$set': {'finished': True}})



def add_default_user(db):
    """
    Add a default user.

    User that will be added::

        {
            'name': 'Default User',
            'email': 'default_user@example.com',
            'permissions': ['USER_MANAGEMENT']
        }

    Api_key: 1234
    Auth_id: default::default
    """
    logging.info('Attempting to add default user')
    new_user = structure.user()
    api_salt = 'fedcba09'
    new_user.update({'name': 'Default User',
                     'email': 'default_user@example.com',
                     'permissions': ['USER_MANAGEMENT'],
                     'api_key': utils.gen_api_key_hash('1234', api_salt),
                     'api_salt': api_salt,
                     'auth_ids': ['default::default']})

    result = db.users.insert_one(new_user)
    print(result)
    db['db_status'].update_one({'_id': 'init_db'},
                               {'$set': {'user_added': True}})
    logging.info('Default user added')


def check_migrations(db):
    """
    Check if any migrations need to be performed on the db.

    Args:
        config (dict): Configuration for the data tracker
    """
    db_version = db['db_status'].find_one({'_id': 'db_version'})
    if db_version['version'] > DB_VERSION:
        logging.critical('The database is newer than the software')
        sys.exit(1)
    elif db_version['version'] == DB_VERSION:
        logging.info('The database is up-to-date')

    for i in range(db_version['version'], DB_VERSION):
        logging.info('Database migration for version %d to %d starting', i, i+1)
        MIGRATIONS[i](db)

#!/usr/bin/env python3

import pymongo

from settings import SETTINGS

def connect():
    """
    Connect to mongo database.

    Returns:
        db: the mongo db handler

    """
    client = pymongo.MongoClient(SETTINGS['mongo']['host'],
                                 SETTINGS['mongo']['port'],
                                 username = SETTINGS['mongo']['user']
                                 password = SETTINGS['mongo']['password']
    db = client[SETTINGS.mongo_db]
    return db


def get_datasets():
    """
    Get a simplied list of (all) datasets.
    
    Returns:
        dict: 
    """
    db = connect()

import flask
import pymongo

def clean_mongo(response):
    """
    Clean up a mongo response by removing e.g. ObjectId.

    Changes are done in-place

    Args:
        response: a response from mongodb.find() or .find_one() (dict or list)
    """
    if type(response) == list:
        for entry in response:
            del entry['_id']
    if '_id' in response:
        del response['_id']

def get_dbserver():
    "Get the connection to the MongoDB database server."
    return pymongo.MongoClient(
        host=flask.current_app.config['mongo']['host'],
        port=flask.current_app.config['mongo']['port'],
        username=flask.current_app.config['mongo']['user'],
        password=flask.current_app.config['mongo']['password'])


def get_db(dbserver):
    "Get the connection to the MongoDB database."
    return dbserver[flask.current_app.config['mongo']['db']]

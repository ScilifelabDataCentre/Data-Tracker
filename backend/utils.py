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

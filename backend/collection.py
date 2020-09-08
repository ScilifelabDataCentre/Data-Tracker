"""Collection requests."""
import json
import logging

import flask

import structure
import user
import utils

blueprint = flask.Blueprint('collection', __name__)  # pylint: disable=invalid-name


@blueprint.route('/', methods=['GET'])
def list_collection():
    """Provide a simplified list of all available collections."""
    results = list(flask.g.db['collections'].find())
    return utils.response_json({'collections': results})


@blueprint.route('/random/', methods=['GET'])
@blueprint.route('/random/<int:amount>', methods=['GET'])
def get_random(amount: int = 1):
    """
    Retrieve random collection(s).

    Args:
        amount (int): number of requested collections

    Returns:
        flask.Request: json structure for the collection(s)

    """
    results = list(flask.g.db['collections'].aggregate([{'$sample': {'size': amount}}]))

    for result in results:
        # only show editors if editor/admin
        if not flask.g.current_user or\
           (not user.has_permission('DATA_MANAGEMENT') or
            flask.g.current_user['_id'] not in result['editors']):
            logging.debug('Not allowed to access editors field %s', flask.g.current_user)
            del result['editors']

            # return {_id, _title} for datasets
            result['datasets'] = [flask.g.db.datasets.find_one({'_id': dataset},
                                                               {'title': 1})
                                  for dataset in result['datasets']]
    return utils.response_json({'collections': results})


@blueprint.route('/<identifier>/', methods=['GET'])
def get_collection(identifier):
    """
    Retrieve the collection with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted collection

    Returns:
        flask.Request: json structure for the collection

    """
    try:
        uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    result = flask.g.db['collections'].find_one({'_id': uuid})
    if not result:
        return flask.Response(status=404)

    # only show owner if owner/admin
    if not flask.g.current_user or\
       (not user.has_permission('DATA_MANAGEMENT') and
        flask.g.current_user['_id'] not in result['editors']):
        logging.debug('Not allowed to access editors field %s', flask.g.current_user)
        del result['editors']
    else:
        result['editors'] = [utils.user_uuid_data(entry, flask.g.db) for entry in result['editors']]

    # return {_id, _title} for datasets
    result['datasets'] = [flask.g.db.datasets.find_one({'_id': dataset},
                                                       {'title': 1})
                          for dataset in result['datasets']]


    return utils.response_json({'collection': result})


@blueprint.route('/', methods=['POST'])
@user.login_required
def add_collection():  # pylint: disable=too-many-branches
    """
    Add a collection.

    Returns:
        flask.Response: Json structure with the ``_id`` of the collection.
    """
    # create new collection
    collection = structure.collection()

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)

    # indata validation
    validation = utils.basic_check_indata(indata, collection, prohibited=['_id'])
    if not validation[0]:
        flask.abort(status=validation[1])

    if 'title' not in indata:
        flask.abort(status=400)

    if not indata.get('editors'):
        indata['editors'] = [flask.g.current_user['_id']]

    if 'datasets' in indata:
        for i, dataset_uuid_str in enumerate(indata['datasets']):
            dataset_uuid = utils.str_to_uuid(dataset_uuid_str)
            indata['datasets'][i] = dataset_uuid
            # allow new ones only if owner or DATA_MANAGEMENT
            order_info = flask.g.db['orders'].find_one({'datasets': dataset_uuid})
            if not order_info:
                flask.abort(status=400)
            if not user.has_permission('DATA_MANAGEMENT') and\
               flask.g.current_user['_id'] not in order_info['editors'] and\
               flask.g.current_user['_id'] not in order_info['authors'] and\
               flask.g.current_user['_id'] not in order_info['generators'] and\
               flask.g.current_user['_id'] not in order_info['receivers']:
                flask.abort(status=400)

    collection.update(indata)

    # add to db
    result = flask.g.db['collections'].insert_one(collection)
    if not result.acknowledged:
        logging.error('Collection insert failed: %s', collection)
    else:
        utils.make_log('collection', 'add', 'Collection added', collection)

    return utils.response_json({'_id': result.inserted_id})


@blueprint.route('/<identifier>/', methods=['DELETE'])
@user.login_required
def delete_collection(identifier: str):
    """
    Delete a collection.

    Can be deleted only by an owner or user with DATA_MANAGEMENT permissions.

    Args:
        identifier (str): The collection uuid.
    """
    try:
        ds_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    collection = flask.g.db['collections'].find_one({'_id': ds_uuid})
    if not collection:
        flask.abort(status=404)

    # permission check
    if not user.has_permission('DATA_MANAGEMENT') and \
       flask.g.current_user['_id'] not in collection['editors']:
        flask.abort(status=403)

    result = flask.g.db['collections'].delete_one({'_id': ds_uuid})
    if not result.acknowledged:
        logging.error(f'Failed to delete collection {ds_uuid}')
        return flask.Response(status=500)
    utils.make_log('collection', 'delete', 'Deleted collection', data={'_id': ds_uuid})

    return flask.Response(status=200)


@blueprint.route('/<identifier>/', methods=['PATCH'])
@user.login_required
def update_collection(identifier):  # pylint: disable=too-many-branches
    """
    Update a collection.

    Args:
        identifier (str): The collection uuid.

    Returns:
        flask.Response: Status code.
    """
    try:
        collection_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    collection = flask.g.db['collections'].find_one({'_id': collection_uuid})
    if not collection:
        flask.abort(status=404)

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)

    # permission check
    if not user.has_permission('DATA_MANAGEMENT') and \
       flask.g.current_user['_id'] not in collection['editors'] and\
       flask.g.current_user['email'] not in collection['editors']:
        logging.debug('Unauthorized update attempt (collection %s, user %s)',
                      collection_uuid,
                      flask.g.current_user['_id'])
        flask.abort(status=403)

    # indata validation
    validation = utils.basic_check_indata(indata, collection, prohibited=('_id'))
    if not validation[0]:
        flask.abort(status=validation[1])

    if indata.get('owners'):
        for i, owner in enumerate(indata['owners']):
            if utils.is_email(owner):
                owner_info = flask.g.db['users'].find_one({'email': owner})
                if owner_info:
                    indata['owners'][i] = owner_info['_id']

    if 'datasets' in indata:
        for i, dataset_uuid_str in enumerate(indata['datasets']):
            dataset_uuid = utils.str_to_uuid(dataset_uuid_str)
            indata['datasets'][i] = dataset_uuid
            # do not reject existing datasets
            if dataset_uuid in collection['datasets']:
                continue
            # allow new ones only if owner or DATA_MANAGEMENT
            order_info = flask.g.db['orders'].find_one({'datasets': dataset_uuid})
            if not order_info:
                flask.abort(status=400)
            if not user.has_permission('DATA_MANAGEMENT') and\
               order_info['creator'] != flask.g.current_user['_id'] and\
               order_info['receiver'] != flask.g.current_user['_id']:
                flask.abort(status=400)

    is_different = False
    for field in indata:
        if indata[field] != collection[field]:
            is_different = True
            break

    if indata and is_different:
        result = flask.g.db['collections'].update_one({'_id': collection['_id']}, {'$set': indata})
        if not result.acknowledged:
            logging.error('Collection update failed: %s', indata)
        else:
            collection.update(indata)
            utils.make_log('collection', 'edit', 'Collection updated', collection)

    return flask.Response(status=200)


@blueprint.route('/user/', methods=['GET'])
@user.login_required
def list_user_collections():  # pylint: disable=too-many-branches
    """
    List collection owned by the user.

    Returns:
        flask.Response: JSON structure.
    """
    results = list(flask.g.db['collections']
                   .find({'editors': flask.g.current_user['_id']}))
    return utils.response_json({'collections': results})


@blueprint.route('/<identifier>/log/', methods=['GET'])
@user.login_required
def get_collection_log(identifier: str = None):
    """
    Get change logs for the user entry with uuid ``identifier``.

    Can be accessed by owners and admin (DATA_MANAGEMENT).

    Args:
        identifier (str): The uuid of the collection.

    Returns:
        flask.Response: Logs as json.
    """
    try:
        collection_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not user.has_permission('DATA_MANAGEMENT'):
        collection_data = flask.g.db['collections'].find_one({'_id': collection_uuid})
        if not collection_data:
            flask.abort(403)
        if flask.g.current_user['_id'] not in collection_data['editors']:
            flask.abort(403)

    collection_logs = list(flask.g.db['logs'].find({'data_type': 'collection',
                                                    'data._id': collection_uuid}))

    for log in collection_logs:
        del log['data_type']

    utils.incremental_logs(collection_logs)

    return utils.response_json({'entry_id': collection_uuid,
                                'data_type': 'collection',
                                'logs': collection_logs})

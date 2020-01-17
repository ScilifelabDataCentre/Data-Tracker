"""Dataset requests."""

import flask

import structure
import utils
import user


blueprint = flask.Blueprint('datasets', __name__)  # pylint: disable=invalid-name


@blueprint.route('/all', methods=['GET'])
def list_dataset():
    """Provide a simplified list of all available datasets."""
    results = list(flask.g.db['datasets'].find())
    utils.clean_mongo(results)
    return utils.response_json({'datasets': results})


@blueprint.route('/add', methods=['GET'])
@user.steward_required
def add_dataset_get():
    """Provide a basic data structure for adding a dataset."""
    dataset = structure.dataset()
    del dataset['uuid']
    del dataset['timestamp']
    return utils.response_json(dataset)


@blueprint.route('/add', methods=['POST'])
@user.steward_required
def add_dataset_post():
    """Add a dataset."""
    dataset = structure.dataset()
    result = flask.g.db['datasets'].insert_one(dataset)
    inserted = flask.g.db['datasets'].find_one({'_id': result.inserted_id})
    return utils.response_json({'uuid': inserted['uuid']})


@blueprint.route('/random', methods=['GET'])
@blueprint.route('/random/<int:amount>', methods=['GET'])
def get_random_ds(amount: int = 1):
    """
    Retrieve random dataset(s).

    Args:
        amount (int): number of requested datasets

    Returns:
        flask.Request: json structure for the dataset(s)

    """
    results = list(flask.g.db['datasets'].aggregate([{'$sample': {'size': amount}}]))
    utils.clean_mongo(results)
    return utils.response_json({'datasets': results})


@blueprint.route('/<identifier>', methods=['GET'])
def get_dataset(identifier):
    """
    Retrieve the dataset with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted dataset

    Returns:
        flask.Request: json structure for the dataset

    """
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
        result = flask.g.db['datasets'].find_one({'uuid': mongo_uuid})
    except ValueError:
        result = None

    if not result:
        return flask.Response(status=404)
    result['projects'] = [{'title': hit['title'], 'uuid': hit['uuid']}
                          for hit in flask.g.db['projects'].find({'datasets': result['uuid']})]
    utils.clean_mongo(result)
    return utils.response_json({'dataset': result})


@blueprint.route('/<identifier>/delete', methods=['PUT'])
@user.steward_required
def delete_dataset(identifier):
    """Delete a dataset."""
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
    except ValueError:
        return flask.Response(status=404)
    result = flask.g.db['datasets'].delete_one({'uuid': mongo_uuid})
    if result.deleted_count == 0:
        return flask.Response(status=404)
    return flask.Response(status=200)

"""Main app for the Data Tracker."""

import flask

import config
import dataset
import developer
import order
import project
import user
import utils


app = flask.Flask(__name__)  # pylint: disable=invalid-name
app.config.update(config.init())

if app.config['dev_mode']['api']:
    app.register_blueprint(developer.blueprint, url_prefix='/api/developer')

app.register_blueprint(dataset.blueprint, url_prefix='/api/dataset')
app.register_blueprint(order.blueprint, url_prefix='/api/order')
app.register_blueprint(project.blueprint, url_prefix='/api/project')
app.register_blueprint(user.blueprint, url_prefix='/api/user')


@app.before_request
def prepare():
    """Open the database connection and get the current user."""
    if flask.request.method != 'GET':
        utils.verify_csrf_token()
    flask.g.dbserver = utils.get_dbclient(flask.current_app.config)
    flask.g.db = utils.get_db(flask.g.dbserver, flask.current_app.config)
    flask.g.current_user = user.get_current_user()
    flask.g.permissions = flask.g.current_user['permissions'] if flask.g.current_user else None


@app.after_request
def finalize(response):
    """Finalize the response and clean up."""
    # close db connection
    if hasattr(flask.g, 'dbserver'):
        flask.g.dbserver.close()
    # set csrf cookie if not set
    if not flask.request.cookies.get('_csrf_token'):
        response.set_cookie('_csrf_token', utils.gen_csrf_token(), samesite='Lax')
    # add some headers for protection
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/api/')
def api_base():
    """List entities."""
    return flask.jsonify({'entities': ['dataset', 'order', 'project', 'user']})


@app.errorhandler(400)
def error_bad_request(_):
    """Make sure a simple 400 is returned instead of an html page."""
    return flask.Response(status=400)

@app.errorhandler(401)
def error_unauthorized(_):
    """Make sure a simple 401 is returned instead of an html page."""
    return flask.Response(status=401)


@app.errorhandler(403)
def error_forbidden(_):
    """Make sure a simple 403 is returned instead of an html page."""
    return flask.Response(status=403)


@app.errorhandler(404)
def error_not_found(_):
    """Make sure a simple 404 is returned instead of an html page."""
    return flask.Response(status=404)


# to allow coverage check for testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

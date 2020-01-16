"""Main app for the Data Tracker."""

import flask

import config
import dataset
import developer
import projects
import user
import utils


app = flask.Flask(__name__)  # pylint: disable=invalid-name
config.init(app)

if app.config['dev_mode']:
    app.register_blueprint(developer.blueprint, url_prefix='/api/developer')

app.register_blueprint(dataset.blueprint, url_prefix='/api/dataset')
app.register_blueprint(projects.blueprint, url_prefix='/api/project')
app.register_blueprint(user.blueprint, url_prefix='/api/user')


@app.before_request
def prepare():
    """Open the database connection; get the current user."""
    if flask.request.method in ('POST', 'PUT', 'DELETE'):
        utils.check_csrf_token()
    flask.g.dbserver = utils.get_dbserver()
    flask.g.db = utils.get_db(flask.g.dbserver)
    flask.g.current_user = user.get_current_user()
    flask.g.current_role = flask.g.current_user['role'] if flask.g.current_user else None


@app.after_request
def finalize(response):
    """Close the database connection."""
    if hasattr(flask.g, 'dbserver'):
        flask.g.dbserver.close()
    # add some headers for protection
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.errorhandler(404)
def not_found(error):
    return flask.Response(status=404)


# to allow coverage check for testing
if __name__ == '__main__':
    app.run(debug=True, port=4444)

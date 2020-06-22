"""Main app for the Data Tracker."""

import logging

import flask

import config
import dataset
import developer
import order
import project
import user
import utils

from authlib.integrations.flask_client import OAuth

app = flask.Flask(__name__)  # pylint: disable=invalid-name
app.config.update(config.init())

if app.config['dev_mode']['api']:
    app.register_blueprint(developer.blueprint, url_prefix='/api/developer')

app.register_blueprint(dataset.blueprint, url_prefix='/api/dataset')
app.register_blueprint(order.blueprint, url_prefix='/api/order')
app.register_blueprint(project.blueprint, url_prefix='/api/project')
app.register_blueprint(user.blueprint, url_prefix='/api/user')


oauth = OAuth(app)
oauth.register('google', client_kwargs={'scope': 'openid profile email'})

@app.before_request
def prepare():
    """Open the database connection and get the current user."""
    flask.g.dbserver = utils.get_dbclient(flask.current_app.config)
    flask.g.db = utils.get_db(flask.g.dbserver, flask.current_app.config)
    if apikey := flask.request.headers.get('X-API-Key'):
        if not (apiuser := flask.request.headers.get('X-API-User')):  # pylint: disable=superfluous-parens
            flask.abort(status=400)
        utils.verify_api_key(apiuser, apikey)
        flask.g.current_user = flask.g.db['users'].find_one({'auth_id': apiuser})
        flask.g.permissions = flask.g.current_user['permissions']
    else:
        if flask.request.method != 'GET':
            utils.verify_csrf_token()
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


@app.route('/api/login/oidc/login/')
def oidc_login():
    """Perform a login using OpenID Connect (e.g. Elixir AAI)."""
    redirect_uri = flask.url_for('oidc_authorize', _external=True)
    logging.debug(f'oauth content: {dir(oauth)}')
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/api/login/oidc/authorize/')
def oidc_authorize():
    """Authorize a login using OpenID Connect (e.g. Elixir AAI)."""
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('account/verify_credentials.json')
    profile = resp.json()
    response = {'token': str(token),
                'resp': str(resp),
                'profile': str(profile)}
    logging.debug(f'response.token: {token}')
    logging.debug(f'response.resp: {resp}')
    logging.debug(f'response.profile: {profile}')

    return flask.redirect('/')


# requests
@app.route('/api/login/apikey/', methods=['POST'])
def key_login():
    """Log in using an apikey."""
    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)

    if 'api-user' not in indata or 'api-key' not in indata:
        logging.debug('API key login - bad keys: %s', indata)
        return flask.Response(status=400)
    utils.verify_api_key(indata['api-user'], indata['api-key'])
    user.do_login(auth_id=indata['api-user'])
    return flask.Response(status=200)


@app.route('/api/logout/')
def logout():
    """Log out the current user."""
    flask.session.clear()
    response = flask.redirect("/", code=302)
    response.set_cookie('_csrf_token', utils.gen_csrf_token(), 0)
    return response


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

import flask

import user


blueprint = flask.Blueprint('developer', __name__)

@blueprint.route('/login/<username>')
def login(username):
    user.do_login(username)
    return flask.Response(status=200)


@app.route('/hello')
def api_hello():
    return flask.jsonify({'test': 'success'})


@app.route('/loginhello')
@user.login_required
def login_hello():
    return flask.jsonify({'test': 'success'})


@app.route('/stewardhello')
@user.steward_required
def steward_hello():
    return flask.jsonify({'test': 'success'})


@app.route('/adminhello')
@user.admin_required
def admin_hello():
    return flask.jsonify({'test': 'success'})

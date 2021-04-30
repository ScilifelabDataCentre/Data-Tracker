"""Routes and functions intended to aid development and testing."""
import copy

import flask

import user

blueprint = flask.Blueprint("developer", __name__)  # pylint: disable=invalid-name


@blueprint.route("/login/<identifier>")
def login(identifier: str):
    """
    Log in without password.

    Args:
        identifer (str): User ``auth_id``.
    """
    res = user.do_login(auth_id=identifier)
    if res:
        response = flask.Response(status=200)
        return response
    return flask.Response(status=500)


@blueprint.route("/hello")
def api_hello():
    """Test request."""
    return flask.jsonify({"test": "success"})


@blueprint.route("/loginhello")
@user.login_required
def login_hello():
    """Test request requiring login."""
    return flask.jsonify({"test": "success"})


@blueprint.route("/hello/<permission>")
def permission_hello(permission: str):
    """
    Test request requiring the given permission.

    Args:
        permission (str): The permission to test for.
    """
    if not user.has_permission(permission):
        flask.abort(status=403)

    return flask.jsonify({"test": "success"})


@blueprint.route("/csrftest", methods=["POST", "PATCH", "POST", "DELETE"])
def csrf_test():
    """Test csrf tokens."""
    return flask.jsonify({"test": "success"})


@blueprint.route("/test_datasets")
def get_added_ds():
    """Get datasets added during testing."""
    added = list(
        flask.g.db["datasets"].find({"description": "Test dataset"}, {"_id": 1})
    )
    return flask.jsonify({"datasets": added})


@blueprint.route("/session")
def list_session():
    """List all session variables."""
    session = copy.deepcopy(flask.session)
    for key in session:
        session[key] = repr(session[key])
    return flask.jsonify(session)


@blueprint.route("/user/me")
def list_current_user():
    """List all session variables."""
    current_user = flask.g.current_user
    for key in current_user:
        current_user[key] = repr(current_user[key])
    return flask.jsonify(current_user)


@blueprint.route("/config")
def list_config():
    """List all session variables."""
    config = copy.deepcopy(flask.current_app.config)
    for key in config:
        config[key] = repr(config[key])
    return flask.jsonify(config)


@blueprint.route("/quit")
def stop_server():
    """Shutdown the flask server."""
    flask.request.environ.get("werkzeug.server.shutdown")()
    return flask.Response(status=200)


def sitemap_builder():
    endpoints = []
    for rule in flask.current_app.url_map.iter_rules():
        methods = ",".join(rule.methods)
        endpoints.append(
            {"endpoint": rule.endpoint, "methods": methods, "route": str(rule)}
        )
    endpoints.sort(key=lambda x: x["route"])
    return endpoints


@blueprint.route("/sitemap")
def list_endpoints_formatted_text():
    """List all endpoints for the app."""
    return flask.jsonify(
        [
            f"{entry['endpoint']:50s} {entry['methods']:25s} {entry['route']}"
            for entry in sitemap_builder()
        ]
    )


@blueprint.route("/sitemap-json")
def list_endpoints_json():
    """List all endpoints for the app."""
    return flask.jsonify({"endpoints": sitemap_builder()})

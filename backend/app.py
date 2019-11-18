import flask

app = flask.Flask('backend')

@app.route('/api/hello')
def api_hello():
    return flask.jsonify({'test': 'value'})

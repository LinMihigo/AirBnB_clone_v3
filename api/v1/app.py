#!/usr/bin/python3
"""app.py"""

from flask import Flask, jsonify
from models import storage
from api.v1.views import app_views

app = Flask(__name__)

# Enable pretty-print JSON responses
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Register blueprints
app.register_blueprint(app_views)


@app.teardown_appcontext
def storage_close(exception=None):
    """Calls storage.close()"""
    storage.close()


@app.errorhandler(404)
def page_not_found(error):
    """Return a json data on 404 page"""
    return jsonify(error="Not found"), 404


if __name__ == "__main__":
    from os import getenv

    host = getenv("HBNB_API_HOST", "0.0.0.0")
    port = int(getenv("HBNB_API_PORT", "5000"))

    app.run(host=host, port=port, threaded=True)

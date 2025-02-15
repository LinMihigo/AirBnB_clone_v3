#!/usr/bin/python3
"""Index route for the API."""

from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status', methods=['GET'])
def index():
    """Returns the status of the API"""
    return jsonify(status="OK")

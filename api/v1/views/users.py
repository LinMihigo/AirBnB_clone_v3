#!/usr/bin/python3
"""View for the User object"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.user import User


@app_views.route('/users', methods=["GET"], strict_slashes=False)
def get_users():
    """Retrieves list of all users"""
    users = storage.all(User)
    dict = [v.to_dict() for k, v in users.items()]
    return jsonify(dict)


@app_views.route('/users', methods=["POST"], strict_slashes=False)
def add_user():
    """Creates a user"""
    if not request.get_json():
        abort(400, description="Not a JSON")
    if "email" not in request.get_json():
        abort(400, description="Missing email")
    if "password" not in request.get_json():
        abort(400, description="Missing password")

    data = request.get_json()
    user = User(**data)
    user.save()
    return jsonify(user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def get_user_id(user_id):
    """Retrieves a user by their id"""
    users = storage.all(User)
    if not "User" + "." + user_id in users.keys():
        abort(404)
    else:
        return jsonify(users["User" + "." + user_id].to_dict())


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id):
    """Updates a user of user_id"""
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    output = storage.all()
    if "User" + "." + user_id in output.keys():
        for k, v in data.items():
            setattr(output["User" + "." + user_id], k, v)
        output["User" + "." + user_id].save()
        return jsonify(output["User" + "." + user_id]), 200
    else:
        abort(404)


@app_views.route("/users/<user_id>", methods=['DELETE'], strict_slashes=False)
def del_user(user_id):
    """Deletes a user"""
    users = storage.all(User)
    if "User" + "." + user_id in users.keys():
        storage.delete(users["User" + "." + user_id])
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)

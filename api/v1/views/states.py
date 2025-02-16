#!/usr/bin/python3
"""
Creates a new view for State objects that handles all default RESTful
API actions
"""
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.state import State


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def handle_states():
    """Retrieves list of all State objects"""
    states = storage.all(State)
    dict = [v.to_dict() for k, v in states.items()]
    return jsonify(dict)


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """Creates a state"""
    if not request.get_json:
        abort(400, description="Not a JSON")
    if not "name" in request.get_json():
        abort(400, description="Missing name")
    data = request.get_json()
    state = State(**data)
    state.save()
    return jsonify(state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state_id(state_id):
    """Retrieves State object of state_id"""
    states = storage.all(State)
    dict = []
    for k, v in states.items():
        if k == "State" + "." + state_id:
            dict = v.to_dict()

    if len(dict) == 0:
        abort(404)
    else:
        return jsonify(dict)


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state_id(state_id):
    """Updates a state obj of state_id"""
    if not request.get_json:
        abort(400, description="Not a JSON")

    data = request.get_json()
    output = storage.all()

    if not "State" + "." + state_id in output.keys():
        abort(404)
    else:
        for key, value in data.items():
            setattr(output["State" + "." + state_id], key, value)
        output["State" + "." + state_id].save()
        return jsonify(output["State" + "." + state_id].to_dict()), 200


@app_views.route('/states/<state_id>', methods=['DELETE'], strict_slashes=False)
def del_state_id(state_id):
    """Deletes a State obj of state_id"""
    states = storage.all(State)
    if "State" + "." + state_id in states.keys():
        storage.delete(states["State" + "." + state_id])
        storage.save()
        return jsonify({})
    else:
        abort(404)

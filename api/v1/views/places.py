#!/usr/bin/python3
"""Creates a new view for Place objects
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_city_places(city_id):
    """Retrieves list of all places in a city"""
    city = storage.get(City, city_id)
    places = storage.all(Place)
    if city_id != city.id:
        abort(404)
    else:
        list = [v.to_dict() for v in places.values() if city_id == v.city_id]
        return jsonify(list)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_places(place_id):
    """Retrieves a place object by its id"""
    place = storage.get(Place, place_id)
    if place:
        return jsonify(place.to_dict())
    else:
        abort(404)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a place with place_id"""
    if not request.get_json():
        abort(400, description="Not a JSON")

    output = storage.all()
    place = storage.get(Place, place_id)
    data = request.get_json()
    ignore_keys = {'id', 'user_id', 'city_id', 'create_at', 'updated_at'}
    if place:
        for k, v in data.items():
            if k not in ignore_keys:
                setattr(output["Place" + "." + place_id], k, v)
        output["Place" + "." + place_id].save()
        return jsonify(output["Place" + "." + place_id].to_dict()), 200
    else:
        abort(404)


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def del_place(place_id):
    """Delete a place with place_id"""
    output = storage.all()
    place = storage.get(Place, place_id)
    if place:
        storage.delete(output["Place" + "." + place_id])
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


@app_views.route('/cities/<city_id>/places', methods=["POST"],
                 strict_slashes=False)
def add_place(city_id):
    """Creates a place in a city of city_id"""
    if not request.get_json():
        abort(400, description="Not a JSON")
    if "user_id" not in request.get_json():
        abort(400, description="Missing user_id")
    if "name" not in request.get_json():
        abort(400, description="Missing name")

    city = storage.get(City, city_id)
    data = request.get_json()
    user = storage.get(User, data["user_id"])
    if not city or not user:
        abort(404)
    else:
        data["city_id"] = city_id
        place = Place(**data)
        place.save()
        return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=["POST"], strict_slashes=False)
def places_search():
    """Retrieves all Place objects depending on the JSON request body."""
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    places = set()  # Use a set to avoid duplicates

    # If no filters are provided, return all places
    if not data or all(len(data.get(key, [])) == 0
                       for key in ["states", "cities", "amenities"]):
        return jsonify([place.to_dict()
                       for place in storage.all(Place).values()])

    # Retrieve states and cities from the request
    states = data.get("states", [])
    cities = data.get("cities", [])

    # Retrieve places from states (including all their cities)
    city_ids = set()
    for state_id in states:
        state = storage.get(State, state_id)
        if state:
            city_ids.update(city.id for city in state.cities)

    # Add explicitly listed cities (avoid duplicate processing)
    for city_id in cities:
        city_ids.add(city_id)

    # Retrieve places from collected city IDs
    for city_id in city_ids:
        city = storage.get(City, city_id)
        if city:
            places.update(city.places)

    # Filter places by amenities (if specified)
    if "amenities" in data and data["amenities"]:
        amenity_ids = set(data["amenities"])
        filtered_places = []
        for place in places:
            place_amenities = {amenity.id for amenity in place.amenities}
            # Place must have ALL amenities
            if amenity_ids.issubset(place_amenities):
                filtered_places.append(place)
        places = filtered_places

    return jsonify([place.to_dict() for place in places])

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
    """Retrieves all Place objects based on JSON request body."""
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()

    # If no filters are provided, return all places
    if not data or all(len(data.get(key, [])) == 0
                       for key in ["states", "cities", "amenities"]):
        places = storage.all(Place).values()
        return jsonify([place.to_dict() for place in places])

    place_list = set()

    # Fetch places based on states
    if "states" in data and data["states"]:
        for state_id in data["states"]:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    place_list.update(city.places)

    # Fetch places based on cities
    if "cities" in data and data["cities"]:
        for city_id in data["cities"]:
            city = storage.get(City, city_id)
            if city:
                place_list.update(city.places)

    # Convert set to list for further processing
    place_list = list(place_list)

    # Filter places based on amenities
    if "amenities" in data and data["amenities"]:
        amenities_ids = set(data["amenities"])
        filtered_places = []
        for place in place_list:
            place_amenities = {amenity.id for amenity in place.amenities}
            if amenities_ids.issubset(place_amenities):
                filtered_places.append(place)
        place_list = filtered_places

    return jsonify([place.to_dict() for place in place_list])

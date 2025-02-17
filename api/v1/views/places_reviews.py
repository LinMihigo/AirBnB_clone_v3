#!/usr/bin/python3
"""
Creates a new view for Review objects that handles all default RESTFul
API actions.
"""
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.review import Review
from models.user import User  # Ensure User is imported for validation
from api.v1.views import app_views


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_reviews(place_id):
    """Retrieves the list of all review objects of a Place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)  # Return 404 if place does not exist

    # Return list of reviews as JSON
    return jsonify([review.to_dict() for review in place.reviews])


@app_views.route('/reviews/<review_id>', methods=['GET'], strict_slashes=False)
def get_review(review_id):
    """Retrieves a single Review object"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """Deletes a Review object."""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    storage.delete(review)
    storage.save()
    return jsonify({}), 200  # Return empty dictionary on success


@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def create_review(place_id):
    """Creates a new review for a specific place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)  # Return 404 if place does not exist

    # Ensure request data is JSON
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()

    # Validate that 'user_id' is provided
    if 'user_id' not in data:
        abort(400, description="Missing user_id")

    # Validate if user exists
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)

    # Validate that 'text' field is provided
    if 'text' not in data:
        abort(400, description="Missing text")

    # Create and save new review
    new_review = Review(place_id=place_id, user_id=data['user_id'],
                        text=data['text'])
    storage.new(new_review)
    storage.save()
    return jsonify(new_review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['PUT'], strict_slashes=False)
def update_review(review_id):
    """Updates an existing Review object"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    # Ensure request data is JSON
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    ignore_keys = {'id', 'user_id', 'place_id', 'created_at', 'updated_at'}

    # Update only allowed attributes
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(review, key, value)

    storage.save()
    return jsonify(review.to_dict()), 200

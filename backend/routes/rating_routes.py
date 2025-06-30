from flask import Blueprint, request, jsonify
from models.rating import Rating
from extensions import db
import time

ratings_bp = Blueprint('ratings', __name__)

@ratings_bp.route('/rate', methods=['POST'])
def rate_movie():
    data = request.get_json()
    userId = data.get('userId')
    movieId = data.get('movieId')
    rating_value = data.get('rating')

    if not all([userId, movieId, rating_value]):
        return jsonify({'message': 'Missing data'}), 400

    new_rating = Rating(userId=userId, movieId=movieId, rating=rating_value, timestamp=int(time.time()))
    db.session.add(new_rating)
    db.session.commit()

    return jsonify({'message': 'Rating submitted successfully'}), 201

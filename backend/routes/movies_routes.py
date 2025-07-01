from flask import Blueprint, jsonify
from models.movie import Movie

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    movies_list = [{'movieId': movie.movieId, 'title': movie.title, 'genres': movie.genres} for movie in movies]
    return jsonify({'movies': movies_list}), 200

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    return jsonify({
        'movieId': movie.movieId,
        'title': movie.title,
        'genres': movie.genres
    }), 200

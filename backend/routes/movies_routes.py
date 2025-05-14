from flask import Blueprint, jsonify
from models.movie import Movie

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    movies_list = [{'movieId': movie.movieId, 'title': movie.title, 'genres': movie.genres} for movie in movies]
    return jsonify(movies_list), 200

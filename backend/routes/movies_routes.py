from flask import Blueprint, jsonify
from models.movie import Movie
from models.user_interaction import UserInteraction

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    movies_list = []
    for movie in movies:
        # Lấy các bình luận từ UserInteraction
        comments = UserInteraction.query.filter_by(movieId=movie.movieId, type='Comment').all()
        comments_list = [
            {
                'userId': c.userId,
                'content': c.content,
                'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for c in comments
        ]
        movies_list.append({
            'movieId': movie.movieId,
            'title': movie.title,
            'genres': movie.genres,
            'comments': comments_list
        })
    return jsonify({'movies': movies_list}), 200

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    # Lấy các bình luận từ UserInteraction
    comments = UserInteraction.query.filter_by(movieId=movie.movieId, type='Comment').all()
    comments_list = [
        {
            'userId': c.userId,
            'content': c.content,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for c in comments
    ]
    return jsonify({
        'movieId': movie.movieId,
        'title': movie.title,
        'genres': movie.genres,
        'comments': comments_list
    }), 200

@movies_bp.route('/movie/<int:user_id>', methods=['GET'])
def get_shared_movies_by_user(user_id):
    # Lấy các movieId mà user đã share
    shares = UserInteraction.query.filter_by(userId=user_id, type='Share').all()
    movie_ids = [s.movieId for s in shares]
    movies = Movie.query.filter(Movie.movieId.in_(movie_ids)).all() if movie_ids else []
    movies_list = [
        {
            'movieId': movie.movieId,
            'title': movie.title,
            'genres': movie.genres
        } for movie in movies
    ]
    return jsonify({'shared_movies': movies_list}), 200

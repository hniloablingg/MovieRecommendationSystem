from flask import Blueprint, request, jsonify
from models.user_interaction import UserInteraction
from models.user import User
from models.movie import Movie
from extensions import db
from datetime import datetime

shares_bp = Blueprint('shares', __name__)

@shares_bp.route('/share', methods=['POST'])
def share_movie():
    """Share a movie to a platform"""
    data = request.get_json()
    
    userId = data.get('userId')
    movieId = data.get('movieId')
    platform = data.get('platform')  # facebook, twitter, email, link, etc.
    
    if not all([userId, movieId, platform]):
        return jsonify({'message': 'Missing required fields: userId, movieId, platform'}), 400
    
    # Validate user and movie exist
    user = User.query.get(userId)
    movie = Movie.query.get(movieId)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    # Validate platform
    valid_platforms = ['facebook', 'twitter', 'email', 'link', 'whatsapp', 'telegram']
    if platform.lower() not in valid_platforms:
        return jsonify({'message': f'Invalid platform. Supported platforms: {valid_platforms}'}), 400
    
    # Create new share record (lưu platform vào content nếu muốn)
    share = UserInteraction(
        userId=userId,
        movieId=movieId,
        type='Share',
        content=platform.lower(),
        created_at=datetime.utcnow()
    )
    
    db.session.add(share)
    db.session.commit()
    
    # Generate share URL/content based on platform
    base_url = "http://127.0.0.1:5000"
    movie_url = f"{base_url}/movies/{movieId}"
    
    share_content = {
        'facebook': f"Check out this amazing movie: {movie.title} ({movie.genres}) - {movie_url}",
        'twitter': f"🎬 Just discovered: {movie.title} ({movie.genres}) {movie_url} #MovieRecommendation",
        'email': f"Subject: Movie Recommendation - {movie.title}\n\nHi,\n\nI wanted to recommend this great movie: {movie.title}\nGenres: {movie.genres}\nWatch more details: {movie_url}\n\nEnjoy!",
        'link': movie_url,
        'whatsapp': f"🎬 Movie recommendation: *{movie.title}* ({movie.genres}) - {movie_url}",
        'telegram': f"🎬 Movie recommendation: {movie.title} ({movie.genres})\n{movie_url}"
    }
    
    return jsonify({
        'message': 'Movie shared successfully',
        'id': share.id,
        'platform': platform,
        'movieTitle': movie.title,
        'shareContent': share_content.get(platform.lower(), movie_url),
        'shared_at': share.created_at.isoformat()
    }), 201

@shares_bp.route('/movie/<int:movie_id>/shares', methods=['GET'])
def get_movie_shares(movie_id):
    """Get share statistics for a specific movie"""
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    shares = UserInteraction.query.filter_by(movieId=movie_id, type='Share').all()
    
    # Group by platform (lấy từ content)
    platform_stats = {}
    total_shares = len(shares)
    
    for share in shares:
        platform = share.content or 'unknown'
        if platform not in platform_stats:
            platform_stats[platform] = 0
        platform_stats[platform] += 1
    
    return jsonify({
        'movieId': movie_id,
        'movieTitle': movie.title,
        'totalShares': total_shares,
        'platformStats': platform_stats,
        'shares': [{
            'id': share.id,
            'userId': share.userId,
            'platform': share.content,
            'shared_at': share.created_at.isoformat()
        } for share in shares]
    }), 200

@shares_bp.route('/user/<int:user_id>/shares', methods=['GET'])
def get_user_shares(user_id):
    """Get all shares by a specific user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    shares = UserInteraction.query.filter_by(userId=user_id, type='Share').order_by(UserInteraction.created_at.desc()).all()
    
    shares_data = []
    for share in shares:
        movie = Movie.query.get(share.movieId)
        shares_data.append({
            'id': share.id,
            'movieId': share.movieId,
            'movieTitle': movie.title if movie else 'Unknown',
            'platform': share.content,
            'shared_at': share.created_at.isoformat()
        })
    
    return jsonify({
        'userId': user_id,
        'username': user.username,
        'shares': shares_data,
        'totalShares': len(shares_data)
    }), 200

@shares_bp.route('/popular', methods=['GET'])
def get_popular_shares():
    """Get most shared movies"""
    from sqlalchemy import func
    
    popular_movies = db.session.query(
        UserInteraction.movieId,
        func.count(UserInteraction.id).label('share_count')
    ).filter_by(type='Share').group_by(UserInteraction.movieId).order_by(func.count(UserInteraction.id).desc()).limit(10).all()
    
    popular_data = []
    for movie_id, share_count in popular_movies:
        movie = Movie.query.get(movie_id)
        if movie:
            popular_data.append({
                'movieId': movie_id,
                'movieTitle': movie.title,
                'genres': movie.genres,
                'shareCount': share_count
            })
    
    return jsonify({
        'popularMovies': popular_data
    }), 200 
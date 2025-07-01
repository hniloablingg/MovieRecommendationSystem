from flask import Blueprint, request, jsonify
from models.movie import Comment
from models.user import User
from models.movie import Movie
from extensions import db
from datetime import datetime

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/add', methods=['POST'])
def add_comment():
    """Add a new comment for a movie"""
    data = request.get_json()
    
    userId = data.get('userId')
    movieId = data.get('movieId')
    content = data.get('content')
    
    if not all([userId, movieId, content]):
        return jsonify({'message': 'Missing required fields: userId, movieId, content'}), 400
    
    # Validate user and movie exist
    user = User.query.get(userId)
    movie = Movie.query.get(movieId)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    # Create new comment
    comment = Comment(
        userId=userId,
        movieId=movieId,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added successfully',
        'commentId': comment.commentId,
        'created_at': comment.created_at.isoformat()
    }), 201

@comments_bp.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_comments(movie_id):
    """Get all comments for a specific movie"""
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    comments = Comment.query.filter_by(movieId=movie_id).order_by(Comment.created_at.desc()).all()
    
    comments_data = []
    for comment in comments:
        user = User.query.get(comment.userId)
        comments_data.append({
            'commentId': comment.commentId,
            'userId': comment.userId,
            'username': user.username if user else 'Unknown',
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        })
    
    return jsonify({
        'movieId': movie_id,
        'movieTitle': movie.title,
        'comments': comments_data,
        'total_comments': len(comments_data)
    }), 200

@comments_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_comments(user_id):
    """Get all comments by a specific user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    comments = Comment.query.filter_by(userId=user_id).order_by(Comment.created_at.desc()).all()
    
    comments_data = []
    for comment in comments:
        movie = Movie.query.get(comment.movieId)
        comments_data.append({
            'commentId': comment.commentId,
            'movieId': comment.movieId,
            'movieTitle': movie.title if movie else 'Unknown',
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        })
    
    return jsonify({
        'userId': user_id,
        'username': user.username,
        'comments': comments_data,
        'total_comments': len(comments_data)
    }), 200

@comments_bp.route('/delete/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a specific comment"""
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200 
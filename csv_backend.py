#!/usr/bin/env python3
"""
CSV-Based Movie Recommendation System
No database required - works entirely with CSV files
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import pickle
import os
from datetime import datetime
from collections import defaultdict
import time

app = Flask(__name__)
CORS(app)

# Global data storage
movies_data = []
users_data = []
ratings_data = []
tags_data = []
comments_data = []
shares_data = []

# Load recommendation model
model_data = None
model_type = None

def load_csv_data():
    """Load all data from CSV files"""
    global movies_data, users_data, ratings_data, tags_data
    
    try:
        # Load movies
        with open('model/data/movies.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            movies_data = list(reader)
        print(f"✅ Loaded {len(movies_data)} movies")
        
        # Load users  
        with open('model/data/users.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            users_data = list(reader)
        print(f"✅ Loaded {len(users_data)} users")
        
        # Load ratings
        with open('model/data/ratings.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ratings_data = list(reader)
        print(f"✅ Loaded {len(ratings_data)} ratings")
        
        # Load tags
        with open('model/data/tags.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tags_data = list(reader)
        print(f"✅ Loaded {len(tags_data)} tags")
        
        return True
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")
        return False

def load_model():
    """Load recommendation model"""
    global model_data, model_type
    
    try:
        model_paths = [
            'model/cf_model.pkl',
            'cf_model.pkl'
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                if isinstance(model_data, tuple):
                    model_type = "pandas"
                    print("✅ Pandas-style model loaded")
                else:
                    model_type = "simple"
                    print("✅ Simple model loaded")
                return True
        
        print("⚠️  No model found")
        return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

# API Routes

@app.route('/movies/', methods=['GET'])
def get_movies():
    """Get all movies"""
    movies = []
    for movie in movies_data:
        movies.append({
            'movieId': int(movie['movieId']),
            'title': movie['title'],
            'genres': movie['genres']
        })
    return jsonify({'movies': movies}), 200

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    """Get movie by ID"""
    for movie in movies_data:
        if int(movie['movieId']) == movie_id:
            return jsonify({
                'movieId': movie_id,
                'title': movie['title'],
                'genres': movie['genres']
            }), 200
    
    return jsonify({'message': 'Movie not found'}), 404

@app.route('/ratings/rate', methods=['POST'])
def rate_movie():
    """Add a new rating"""
    data = request.get_json()
    
    userId = data.get('userId')
    movieId = data.get('movieId')
    rating_value = data.get('rating')
    
    if not all([userId, movieId, rating_value]):
        return jsonify({'message': 'Missing data'}), 400
    
    # Add to in-memory data
    new_rating = {
        'userId': str(userId),
        'movieId': str(movieId),
        'rating': str(rating_value),
        'timestamp': str(int(time.time()))
    }
    ratings_data.append(new_rating)
    
    # Save to CSV file
    try:
        with open('model/data/ratings.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['userId', 'movieId', 'rating', 'timestamp'])
            writer.writerow(new_rating)
    except Exception as e:
        print(f"Error saving rating to CSV: {e}")
    
    return jsonify({'message': 'Rating submitted successfully'}), 201

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get movie recommendations"""
    if model_data is None:
        return jsonify({
            'message': 'Model not available. Please train the model first.',
            'instructions': 'Run: python simple_setup.py'
        }), 503
    
    try:
        if model_type == "pandas":
            # Use pandas-style model
            similarity_matrix, user_item_matrix = model_data
            
            if isinstance(user_item_matrix, dict):
                if user_id not in user_item_matrix:
                    return jsonify({'message': 'User not found'}), 404
                
                # Simple recommendation logic for dict-based matrix
                user_ratings = user_item_matrix[user_id]
                all_movies = set()
                for ratings in user_item_matrix.values():
                    all_movies.update(ratings.keys())
                
                # Find movies user hasn't rated
                unrated_movies = [mid for mid in all_movies if user_ratings.get(mid, 0) == 0]
                
                # Simple scoring: recommend popular movies
                movie_scores = defaultdict(float)
                for movie_id in unrated_movies[:50]:  # Limit for performance
                    total_rating = 0
                    count = 0
                    for uid, ratings in user_item_matrix.items():
                        if ratings.get(movie_id, 0) > 0:
                            total_rating += ratings[movie_id]
                            count += 1
                    if count > 0:
                        movie_scores[movie_id] = total_rating / count
                
                # Get top 5
                sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                top_movie_ids = [int(mid) for mid, score in sorted_movies]
            
            else:
                # Handle pandas DataFrame case
                top_movie_ids = [1, 2, 3, 4, 5]  # Fallback
        
        elif model_type == "simple":
            # Use simple model
            top_movie_ids = model_data.recommend(user_id, top_n=5)
        
        else:
            return jsonify({'message': 'Unknown model type'}), 500
        
        return jsonify({'recommended_movie_ids': top_movie_ids}), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Error generating recommendations',
            'error': str(e)
        }), 500

@app.route('/comments/add', methods=['POST'])
def add_comment():
    """Add a new comment"""
    data = request.get_json()
    
    userId = data.get('userId')
    movieId = data.get('movieId')
    content = data.get('content')
    
    if not all([userId, movieId, content]):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Find user and movie to validate
    user_exists = any(int(u['userId']) == userId for u in users_data)
    movie_exists = any(int(m['movieId']) == movieId for m in movies_data)
    
    if not user_exists:
        return jsonify({'message': 'User not found'}), 404
    if not movie_exists:
        return jsonify({'message': 'Movie not found'}), 404
    
    # Add comment
    comment_id = len(comments_data) + 1
    new_comment = {
        'commentId': comment_id,
        'userId': userId,
        'movieId': movieId,
        'content': content,
        'created_at': datetime.utcnow().isoformat()
    }
    comments_data.append(new_comment)
    
    return jsonify({
        'message': 'Comment added successfully',
        'commentId': comment_id,
        'created_at': new_comment['created_at']
    }), 201

@app.route('/comments/movie/<int:movie_id>', methods=['GET'])
def get_movie_comments(movie_id):
    """Get all comments for a movie"""
    movie = next((m for m in movies_data if int(m['movieId']) == movie_id), None)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    movie_comments = [c for c in comments_data if c['movieId'] == movie_id]
    
    comments_data_formatted = []
    for comment in movie_comments:
        user = next((u for u in users_data if int(u['userId']) == comment['userId']), None)
        comments_data_formatted.append({
            'commentId': comment['commentId'],
            'userId': comment['userId'],
            'username': user['username'] if user else 'Unknown',
            'content': comment['content'],
            'created_at': comment['created_at']
        })
    
    return jsonify({
        'movieId': movie_id,
        'movieTitle': movie['title'],
        'comments': comments_data_formatted,
        'total_comments': len(comments_data_formatted)
    }), 200

@app.route('/shares/share', methods=['POST'])
def share_movie():
    """Share a movie"""
    data = request.get_json()
    
    userId = data.get('userId')
    movieId = data.get('movieId')
    platform = data.get('platform')
    
    if not all([userId, movieId, platform]):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user_exists = any(int(u['userId']) == userId for u in users_data)
    movie = next((m for m in movies_data if int(m['movieId']) == movieId), None)
    
    if not user_exists:
        return jsonify({'message': 'User not found'}), 404
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404
    
    valid_platforms = ['facebook', 'twitter', 'email', 'link', 'whatsapp', 'telegram']
    if platform.lower() not in valid_platforms:
        return jsonify({'message': f'Invalid platform. Supported: {valid_platforms}'}), 400
    
    # Add share
    share_id = len(shares_data) + 1
    new_share = {
        'shareId': share_id,
        'userId': userId,
        'movieId': movieId,
        'platform': platform.lower(),
        'shared_at': datetime.utcnow().isoformat()
    }
    shares_data.append(new_share)
    
    # Generate share content
    base_url = "http://127.0.0.1:5000"
    movie_url = f"{base_url}/movies/{movieId}"
    
    share_content = {
        'facebook': f"Check out this amazing movie: {movie['title']} ({movie['genres']}) - {movie_url}",
        'twitter': f"🎬 Just discovered: {movie['title']} ({movie['genres']}) {movie_url} #MovieRecommendation",
        'email': f"Subject: Movie Recommendation - {movie['title']}\\n\\nHi,\\n\\nI wanted to recommend this great movie: {movie['title']}\\nGenres: {movie['genres']}\\nWatch more details: {movie_url}\\n\\nEnjoy!",
        'link': movie_url,
        'whatsapp': f"🎬 Movie recommendation: *{movie['title']}* ({movie['genres']}) - {movie_url}",
        'telegram': f"🎬 Movie recommendation: {movie['title']} ({movie['genres']})\\n{movie_url}"
    }
    
    return jsonify({
        'message': 'Movie shared successfully',
        'shareId': share_id,
        'platform': platform,
        'movieTitle': movie['title'],
        'shareContent': share_content.get(platform.lower(), movie_url),
        'shared_at': new_share['shared_at']
    }), 201

@app.route('/shares/popular', methods=['GET'])
def get_popular_shares():
    """Get most shared movies"""
    share_counts = defaultdict(int)
    
    for share in shares_data:
        share_counts[share['movieId']] += 1
    
    # Sort by share count
    popular_movies = sorted(share_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    popular_data = []
    for movie_id, share_count in popular_movies:
        movie = next((m for m in movies_data if int(m['movieId']) == movie_id), None)
        if movie:
            popular_data.append({
                'movieId': movie_id,
                'movieTitle': movie['title'],
                'genres': movie['genres'],
                'shareCount': share_count
            })
    
    return jsonify({'popularMovies': popular_data}), 200

@app.route('/tags/movie/<int:movie_id>', methods=['GET'])
def get_movie_tags(movie_id):
    """Get tags for a specific movie"""
    movie_tags = [t for t in tags_data if int(t['movieId']) == movie_id]
    
    # Count tag frequency
    tag_counts = defaultdict(int)
    for tag in movie_tags:
        tag_counts[tag['tag']] += 1
    
    # Sort by frequency
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    return jsonify({
        'movieId': movie_id,
        'tags': [{'tag': tag, 'count': count} for tag, count in sorted_tags],
        'total_tags': len(movie_tags)
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'CSV-based Movie Recommendation System is running',
        'data_loaded': {
            'movies': len(movies_data),
            'users': len(users_data), 
            'ratings': len(ratings_data),
            'tags': len(tags_data),
            'comments': len(comments_data),
            'shares': len(shares_data)
        },
        'model_loaded': model_data is not None,
        'model_type': model_type
    }), 200

@app.route('/comments/user/<int:user_id>', methods=['GET'])
def get_user_comments(user_id):
    user_comments = [c for c in comments_data if c['userId'] == user_id]
    comments_data_formatted = []
    for comment in user_comments:
        movie = next((m for m in movies_data if int(m['movieId']) == comment['movieId']), None)
        comments_data_formatted.append({
            'commentId': comment['commentId'],
            'movieId': comment['movieId'],
            'movieTitle': movie['title'] if movie else 'Unknown',
            'content': comment['content'],
            'created_at': comment['created_at']
        })
    return jsonify({'comments': comments_data_formatted}), 200

@app.route('/shares/user/<int:user_id>/shares', methods=['GET'])
def get_user_shares(user_id):
    user_shares = [s for s in shares_data if s['userId'] == user_id]
    shares_data_formatted = []
    for share in user_shares:
        movie = next((m for m in movies_data if int(m['movieId']) == share['movieId']), None)
        shares_data_formatted.append({
            'shareId': share['shareId'],
            'movieId': share['movieId'],
            'movieTitle': movie['title'] if movie else 'Unknown',
            'platform': share['platform'],
            'shared_at': share['shared_at']
        })
    return jsonify({'shares': shares_data_formatted}), 200

if __name__ == '__main__':
    print("""
🎬 =============================================== 🎬
    CSV-BASED MOVIE RECOMMENDATION SYSTEM
🎬 =============================================== 🎬
""")
    
    # Load data
    print("📊 Loading CSV data...")
    if load_csv_data():
        print("✅ All CSV data loaded successfully!")
    else:
        print("❌ Failed to load CSV data")
        exit(1)
    
    # Load model
    print("🤖 Loading recommendation model...")
    load_model()
    
    print("🚀 Starting server at http://127.0.0.1:5000")
    print("🌐 Open frontend/index.html in browser")
    print("📚 Available endpoints:")
    print("  - GET  /health")
    print("  - GET  /movies/")
    print("  - POST /ratings/rate")
    print("  - GET  /recommendations/<user_id>")
    print("  - POST /comments/add")
    print("  - POST /shares/share")
    print("  - GET  /tags/movie/<movie_id>")
    print("-" * 60)
    
    app.run(debug=True) 
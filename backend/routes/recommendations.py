from flask import Blueprint, jsonify
import pickle
import os

recommendations_bp = Blueprint('recommendations', __name__)

# Try to load the model 
model_data = None
model_type = None

try:
    # Try to load model from different possible locations
    model_paths = [
        os.path.join('..', 'model', 'cf_model.pkl'),
        'cf_model.pkl',
        os.path.join('model', 'cf_model.pkl')
    ]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Check if it's pandas-style data (tuple) or simple model (object)
            if isinstance(model_data, tuple):
                similarity_matrix, user_item_matrix = model_data
                model_type = "pandas"
                print("✅ Pandas-style model loaded successfully!")
            else:
                # It's a simple model object
                model_type = "simple"
                print("✅ Simple model loaded successfully!")
            break
    
    if model_data is None:
        print("⚠️  No model file found")
        
except Exception as e:
    print(f"❌ Failed to load model: {e}")

@recommendations_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    if model_data is None:
        return jsonify({
            'message': 'Model not available. Please train the model first.',
            'instructions': 'Run: python simple_setup.py or cd model && python train.py'
        }), 503
    
    try:
        if model_type == "pandas":
            # Use pandas-style model
            similarity_matrix, user_item_matrix = model_data
            
            if user_id not in user_item_matrix:
                return jsonify({'message': 'User not found'}), 404

            # Convert to list for indexing
            user_ids = list(user_item_matrix.keys()) if isinstance(user_item_matrix, dict) else user_item_matrix.index
            
            if user_id not in user_ids:
                return jsonify({'message': 'User not found'}), 404
            
            user_index = user_ids.index(user_id) if isinstance(user_ids, list) else user_item_matrix.index.get_loc(user_id)
            user_vector = similarity_matrix[user_index]
            similar_users = sorted(range(len(user_vector)), key=lambda i: user_vector[i], reverse=True)[1:11]

            # Calculate movie scores
            if isinstance(user_item_matrix, dict):
                # Dictionary-based user_item_matrix
                all_movies = set()
                for user_ratings in user_item_matrix.values():
                    all_movies.update(user_ratings.keys())
                
                movie_scores = {}
                for movie_id in all_movies:
                    if user_item_matrix[user_id].get(movie_id, 0) == 0:  # User hasn't rated
                        score = 0
                        count = 0
                        for similar_user_idx in similar_users:
                            similar_user_id = user_ids[similar_user_idx]
                            rating = user_item_matrix[similar_user_id].get(movie_id, 0)
                            if rating > 0:
                                score += rating
                                count += 1
                        if count > 0:
                            movie_scores[movie_id] = score / count
                
                top_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                top_movie_ids = [movie_id for movie_id, score in top_movies]
            
            else:
                # Pandas-style user_item_matrix
                movie_scores = user_item_matrix.iloc[similar_users].mean(axis=0)
                user_seen_movies = user_item_matrix.loc[user_id]
                movie_scores = movie_scores[user_seen_movies == 0]
                top_movie_ids = movie_scores.sort_values(ascending=False).head(5).index.tolist()

        elif model_type == "simple":
            # Use simple model
            top_movie_ids = model_data.recommend(user_id, top_n=5)
        
        else:
            return jsonify({'message': 'Unknown model type'}), 500

        return jsonify({'recommended_movie_ids': top_movie_ids}), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Error generating recommendations',
            'error': str(e),
            'model_type': model_type
        }), 500

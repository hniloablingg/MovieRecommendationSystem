from flask import Blueprint, jsonify
import pickle
import pandas as pd

recommendations_bp = Blueprint('recommendations', __name__)
 
with open('./../model/cf_model.pkl', 'rb') as f:
    model_data = pickle.load(f)
    similarity_matrix, user_item_matrix = model_data

@recommendations_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    if user_id not in user_item_matrix.index:
        return jsonify({'message': 'User not found'}), 404

    user_vector = similarity_matrix[user_id - 1]
    similar_users = user_vector.argsort()[::-1][1:]

    movie_scores = user_item_matrix.iloc[similar_users].mean(axis=0)
    user_seen_movies = user_item_matrix.loc[user_id]
    movie_scores = movie_scores[user_seen_movies == 0]

    top_movies = movie_scores.sort_values(ascending=False).head(5).index.tolist()

    return jsonify({'recommended_movie_ids': top_movies}), 200

import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np

class CollaborativeFilteringModel:
    def __init__(self):
        self.model = None  # Will store the similarity matrix
        self.user_item_matrix = None  # Will store the user-item matrix

    def train(self, ratings_df):
        """Train the model by creating the user-item matrix and computing cosine similarity."""
        user_item = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        self.user_item_matrix = user_item
        self.model = cosine_similarity(csr_matrix(user_item))

    def save(self, path):
        """Save the model and user-item matrix to a file."""
        with open(path, 'wb') as f:
            pickle.dump((self.model, self.user_item_matrix), f)

    def load(self, path):
        """Load the model and user-item matrix from a file."""
        with open(path, 'rb') as f:
            self.model, self.user_item_matrix = pickle.load(f)

    def recommend(self, user_id, top_n=5):
        """
        Recommend top_n movies for a given user using weighted average of ratings from similar users.
        
        Args:
            user_id (int): The ID of the user to generate recommendations for.
            top_n (int): Number of recommendations to return.
        
        Returns:
            list: List of movie IDs recommended for the user.
        """
        # Check if user exists in the matrix
        if user_id not in self.user_item_matrix.index:
            return []

        # Get the index of the user in the matrix
        user_idx = self.user_item_matrix.index.get_loc(user_id)

        # Get similarity scores for this user to all other users
        user_similarities = self.model[user_idx]

        # Convert user-item matrix to NumPy array for vectorized operations
        user_item_array = self.user_item_matrix.values

        # Create a binary matrix indicating rated movies (1 if rated, 0 if not)
        rated_array = (user_item_array > 0).astype(float)

        # Compute weighted sum of ratings: similarity_matrix[user_idx] @ user_item_matrix
        weighted_sum = user_similarities @ user_item_array

        # Compute normalization factor: sum of similarities for users who rated each movie
        normalization_factor = user_similarities @ rated_array

        # Compute predicted ratings, handling division by zero (set to 0 if no ratings)
        predicted_ratings = np.where(normalization_factor > 0, weighted_sum / normalization_factor, 0)

        # Get movies the user hasn’t seen (ratings == 0)
        user_ratings = user_item_array[user_idx]
        unseen_movies_idx = np.where(user_ratings == 0)[0]

        # Get predicted ratings for unseen movies
        predicted_ratings_unseen = predicted_ratings[unseen_movies_idx]

        # Sort and get indices of top_n movies
        top_indices = np.argsort(predicted_ratings_unseen)[::-1][:top_n]

        # Map indices back to movie IDs
        top_movies_idx = unseen_movies_idx[top_indices]
        top_movie_ids = self.user_item_matrix.columns[top_movies_idx].tolist()

        return top_movie_ids
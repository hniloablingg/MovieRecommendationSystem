import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

class CollaborativeFilteringModel:
    def __init__(self):
        self.model = None
        self.user_item_matrix = None

    def train(self, ratings_df):
        user_item = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        self.user_item_matrix = user_item
        self.model = cosine_similarity(csr_matrix(user_item))

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump((self.model, self.user_item_matrix), f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.model, self.user_item_matrix = pickle.load(f)

    def recommend(self, user_id, top_n=5):
        user_idx = user_id - 1
        user_similarities = self.model[user_idx]
        similar_users = user_similarities.argsort()[::-1][1:]

        movie_scores = self.user_item_matrix.iloc[similar_users].mean(axis=0)
        user_seen_movies = self.user_item_matrix.iloc[user_idx]
        movie_scores = movie_scores[user_seen_movies == 0]

        return movie_scores.sort_values(ascending=False).head(top_n).index.tolist()

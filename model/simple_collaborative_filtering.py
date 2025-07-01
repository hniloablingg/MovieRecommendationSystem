
import csv
import pickle
from collections import defaultdict
import math

class SimpleCollaborativeFiltering:
    def __init__(self):
        self.user_ratings = defaultdict(dict)
        self.movie_ratings = defaultdict(list)
        self.user_item_matrix = None
        self.similarity_matrix = None
    
    def load_ratings_csv(self):
        """Load ratings from CSV file"""
        try:
            with open('./data/ratings.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user_id = int(row['userId'])
                    movie_id = int(row['movieId'])
                    rating = float(row['rating'])
                    
                    self.user_ratings[user_id][movie_id] = rating
                    self.movie_ratings[movie_id].append((user_id, rating))
            
            print(f"Loaded ratings for {len(self.user_ratings)} users")
            print(f"Loaded ratings for {len(self.movie_ratings)} movies")
            return True
        except Exception as e:
            print(f"Error loading ratings: {e}")
            return False
    
    def cosine_similarity(self, user1_ratings, user2_ratings):
        """Calculate cosine similarity between two users"""
        # Find common movies
        common_movies = set(user1_ratings.keys()) & set(user2_ratings.keys())
        if len(common_movies) == 0:
            return 0
        
        # Calculate cosine similarity
        sum_x2 = sum([user1_ratings[movie]**2 for movie in common_movies])
        sum_y2 = sum([user2_ratings[movie]**2 for movie in common_movies])
        sum_xy = sum([user1_ratings[movie] * user2_ratings[movie] for movie in common_movies])
        
        denominator = math.sqrt(sum_x2) * math.sqrt(sum_y2)
        if denominator == 0:
            return 0
        
        return sum_xy / denominator
    
    def build_similarity_matrix(self):
        """Build user similarity matrix"""
        print("Building similarity matrix...")
        users = list(self.user_ratings.keys())
        n_users = len(users)
        
        # Create similarity matrix
        similarity_matrix = []
        for i, user1 in enumerate(users):
            similarities = []
            for j, user2 in enumerate(users):
                if i == j:
                    similarities.append(1.0)
                else:
                    sim = self.cosine_similarity(self.user_ratings[user1], self.user_ratings[user2])
                    similarities.append(sim)
            similarity_matrix.append(similarities)
        
        self.similarity_matrix = similarity_matrix
        
        # Create user-item matrix (simplified)
        all_movies = set()
        for user_ratings in self.user_ratings.values():
            all_movies.update(user_ratings.keys())
        
        user_item_matrix = {}
        for user_id in users:
            user_item_matrix[user_id] = {}
            for movie_id in all_movies:
                user_item_matrix[user_id][movie_id] = self.user_ratings[user_id].get(movie_id, 0)
        
        self.user_item_matrix = user_item_matrix
        print(f"Built similarity matrix for {n_users} users")
    
    def recommend(self, target_user, top_n=5):
        """Recommend movies for target user"""
        if target_user not in self.user_ratings:
            return []
        
        target_ratings = self.user_ratings[target_user]
        users = list(self.user_ratings.keys())
        
        try:
            user_index = users.index(target_user)
        except ValueError:
            return []
        
        # Get similarities for target user
        user_similarities = self.similarity_matrix[user_index]
        
        # Create list of (user_id, similarity) and sort by similarity
        similar_users = []
        for i, similarity in enumerate(user_similarities):
            if i != user_index and similarity > 0:
                similar_users.append((users[i], similarity))
        
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:10]  # Top 10 similar users
        
        # Get movie recommendations
        movie_scores = defaultdict(float)
        movie_counts = defaultdict(int)
        
        for similar_user, similarity in similar_users:
            for movie_id, rating in self.user_ratings[similar_user].items():
                if movie_id not in target_ratings:  # User hasn't seen this movie
                    movie_scores[movie_id] += similarity * rating
                    movie_counts[movie_id] += 1
        
        # Calculate average scores
        recommendations = []
        for movie_id in movie_scores:
            if movie_counts[movie_id] > 0:
                avg_score = movie_scores[movie_id] / movie_counts[movie_id]
                recommendations.append((movie_id, avg_score))
        
        # Sort and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [movie_id for movie_id, score in recommendations[:top_n]]
    
    def train(self):
        """Train the model"""
        print("Training collaborative filtering model...")
        if not self.load_ratings_csv():
            return False
        
        self.build_similarity_matrix()
        return True
    
    def save(self, filepath):
        """Save the model"""
        try:
            with open(filepath, 'wb') as f:
                # Save the matrices in pandas-like format for compatibility
                model_data = (self.similarity_matrix, self.user_item_matrix)
                pickle.dump(model_data, f)
            print(f"Model saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

if __name__ == "__main__":
    # Create and train model
    model = SimpleCollaborativeFiltering()
    
    if model.train():
        model.save('./cf_model.pkl')
        print("Simple collaborative filtering model ready!")
    else:
        print("Failed to train model")

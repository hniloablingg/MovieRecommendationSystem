#!/usr/bin/env python3
"""
Simple Setup - Movie Recommendation System without pandas/sklearn
"""

import subprocess
import sys
import os
import time

def print_banner():
    print("""
🎬 =============================================== 🎬
    MOVIE RECOMMENDATION SYSTEM (SIMPLE MODE)
🎬 =============================================== 🎬
    """)

def create_simple_collaborative_filtering():
    """Tạo collaborative filtering đơn giản không cần pandas/sklearn"""
    print("🤖 Creating simple collaborative filtering model...")
    
    simple_cf_code = '''
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
'''
    
    # Write simple model to model folder with proper encoding
    with open('model/simple_collaborative_filtering.py', 'w', encoding='utf-8') as f:
        f.write(simple_cf_code)
    
    print("✅ Created simple collaborative filtering model")

def train_simple_model():
    """Train the simple model"""
    print("🤖 Training simple recommendation model...")
    try:
        os.chdir("model")
        subprocess.check_call([sys.executable, "simple_collaborative_filtering.py"])
        os.chdir("..")
        
        # Check if model file was created
        if os.path.exists("model/cf_model.pkl"):
            print("✅ Simple model trained successfully!")
            return True
        else:
            print("❌ Model file not found!")
            return False
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        os.chdir("..")
        return False

def start_backend():
    """Start Flask backend server"""
    print("🚀 Starting backend server...")
    try:
        os.chdir("backend")
        print("✅ Backend starting at http://127.0.0.1:5000")
        print("💡 Press Ctrl+C to stop the server")
        print("🌐 Open frontend/index.html in browser for UI")
        print("-" * 50)
        
        # Start Flask server
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
    finally:
        os.chdir("..")

def show_api_examples():
    """Show API usage examples"""
    print("""
📚 API EXAMPLES FOR TESTING:

1️⃣ RATE A MOVIE:
POST http://127.0.0.1:5000/ratings/rate
{
  "userId": "1",
  "movieId": "1", 
  "rating": "5.0"
}

2️⃣ GET RECOMMENDATIONS:
GET http://127.0.0.1:5000/recommendations/1

3️⃣ ADD COMMENT:
POST http://127.0.0.1:5000/comments/add
{
  "userId": 1,
  "movieId": 1,
  "content": "Great movie!"
}

4️⃣ SHARE MOVIE:
POST http://127.0.0.1:5000/shares/share
{
  "userId": 1,
  "movieId": 1,
  "platform": "facebook"
}

5️⃣ GET ALL MOVIES:
GET http://127.0.0.1:5000/movies/

6️⃣ GET MOVIE COMMENTS:
GET http://127.0.0.1:5000/comments/movie/1
""")

def main():
    """Main setup function"""
    print_banner()
    print("🚨 Simple mode - Works without pandas/sklearn dependencies")
    print("   Uses native Python collaborative filtering")
    print()
    
    # Step 1: Create simple collaborative filtering
    create_simple_collaborative_filtering()
    
    # Step 2: Train model
    model_ok = train_simple_model()
    
    if not model_ok:
        print("\n⚠️  Model training failed, but you can still test other APIs")
    
    # Step 3: Show information
    show_api_examples()
    
    # Step 4: Ask user what to do next
    print("\n" + "="*60)
    print("🎯 SETUP COMPLETE! What would you like to do?")
    print("1. Start Backend Server (recommended)")
    print("2. Show API Examples")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            start_backend()
            break
        elif choice == "2":
            show_api_examples()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter 1-3")

if __name__ == "__main__":
    main() 
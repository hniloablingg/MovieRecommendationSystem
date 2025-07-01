#!/usr/bin/env python3
"""
CSV-Only Data Loading for Movie Recommendation System
No database dependencies - works entirely with CSV files
"""

import pandas as pd
import os

def load_users():
    """Load users from CSV file only"""
    try:
        users_df = pd.read_csv('./data/users.csv')
        users_df = users_df[['userId', 'username']]
        print(f"✅ Loaded {len(users_df)} users from CSV file")
        return users_df
    except Exception as e:
        print(f"❌ Failed to load users from CSV: {e}")
        raise

def load_movies():
    """Load movies from CSV file only"""
    try:
        movies_df = pd.read_csv('./data/movies.csv')
        movies_df = movies_df[['movieId', 'title', 'genres']]
        print(f"✅ Loaded {len(movies_df)} movies from CSV file")
        return movies_df
    except Exception as e:
        print(f"❌ Failed to load movies from CSV: {e}")
        raise

def load_ratings():
    """Load ratings from CSV file only"""
    try:
        ratings_df = pd.read_csv('./data/ratings.csv')
        ratings_df = ratings_df[['userId', 'movieId', 'rating']]
        print(f"✅ Loaded {len(ratings_df)} ratings from CSV file")
        return ratings_df
    except Exception as e:
        print(f"❌ Failed to load ratings from CSV: {e}")
        raise

def split_ratings(ratings_df, test_size=0.2, random_state=42):
    """
    Split rating data into training and testing sets 
    """
    # Shuffle the ratings
    shuffled_ratings = ratings_df.sample(frac=1, random_state=random_state)
    
    # Calculate split index
    split_idx = int(len(shuffled_ratings) * (1 - test_size))
    
    # Split the data
    train_ratings = shuffled_ratings.iloc[:split_idx]
    test_ratings = shuffled_ratings.iloc[split_idx:]
    
    return train_ratings, test_ratings
import pandas as pd

def load_users():
    """
    Load user data from CSV file 
    """
    return pd.read_csv('./data/users.csv')

def load_movies():
    """
    Load movie data from CSV file 
    """
    return pd.read_csv('./data/movies.csv')

def load_ratings():
    """
    Load rating data from CSV file 
    """
    return pd.read_csv('./data/ratings.csv')

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
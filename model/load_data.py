import pandas as pd

def load_users():
    return pd.read_csv('./data/users.csv')

def load_movies():
    return pd.read_csv('./data/movies.csv')

def load_ratings():
    return pd.read_csv('./data/ratings.csv')

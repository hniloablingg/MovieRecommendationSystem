from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from extensions import db
from models import User, Movie, Rating
from routes.user_route import users_bp
from routes.movies_routes import movies_bp
from routes.rating_routes import ratings_bp
from routes.recommendations import recommendations_bp
from sqlalchemy import text 
import csv
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)

    with app.app_context():
        # Check DB connection
        try:
            db.session.execute(text('SELECT 1'))
            print("Connected to PostgreSQL successfully!")
        except Exception as e:
            print("Database connection failed:", e)

        # Create tables
        db.create_all()
        print("Tables created successfully (if not exist)")

        # Load CSV data
        load_users()
        load_movies()
        load_ratings()

    # Register routes
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(movies_bp, url_prefix='/movies')
    app.register_blueprint(ratings_bp, url_prefix='/ratings')
    app.register_blueprint(recommendations_bp, url_prefix='')

    return app


def load_users():
    try: 
        
        with open('./data/users.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not User.query.get(row['userId']):
                    user = User(
                        userId=int(row['userId']),
                        username=row['username'],
                        email=row['email'],
                        password=row['password'],
                        created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                    )
                    db.session.add(user)
            db.session.commit()
            print("Users loaded")
    except Exception as e:
        print("Failed to load users:", e)


def load_movies():
    try:
        with open('./data/movies.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not Movie.query.get(row['movieId']):
                    movie = Movie(
                        movieId=int(row['movieId']),
                        title=row['title'],
                        genres=row['genres']
                    )
                    db.session.add(movie)
            db.session.commit()
            print("Movies loaded")
    except Exception as e:
        print("Failed to load movies:", e)


def load_ratings():
    try:
        with open('./data/ratings.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                rating = Rating(
                    userId=int(row['userId']),
                    movieId=int(row['movieId']),
                    rating=float(row['rating']),
                    timestamp=int(row['timestamp'])
                )
                db.session.add(rating)
            db.session.commit()
            print("Ratings loaded")
    except Exception as e:
        print("Failed to load ratings:", e)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

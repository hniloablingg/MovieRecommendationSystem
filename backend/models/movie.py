from extensions import db
from datetime import datetime

class Movie(db.Model):
    __tablename__ = 'movies'

    movieId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genres = db.Column(db.String(255), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments'
    
    commentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    movie = db.relationship('Movie', backref='comments')

class Share(db.Model):
    __tablename__ = 'shares'
    
    shareId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # facebook, twitter, email, etc.
    shared_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='shares')
    movie = db.relationship('Movie', backref='shares')

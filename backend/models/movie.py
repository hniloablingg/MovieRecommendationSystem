from extensions import db

class Movie(db.Model):
    __tablename__ = 'movies'

    movieId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genres = db.Column(db.String(255), nullable=False)

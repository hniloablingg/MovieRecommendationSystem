from extensions import db
class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)

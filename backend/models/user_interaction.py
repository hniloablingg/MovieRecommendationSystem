from extensions import db
from datetime import datetime

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'Comment' hoặc 'Share'
    content = db.Column(db.Text, nullable=True)      # Nội dung bình luận hoặc null nếu là share
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='interactions')
    movie = db.relationship('Movie', backref='interactions') 
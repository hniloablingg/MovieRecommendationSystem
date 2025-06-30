from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, userId, username, email, password, created_at=None):
        self.userId = userId
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at or datetime.utcnow()

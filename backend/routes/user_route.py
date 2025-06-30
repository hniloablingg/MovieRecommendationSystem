from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from extensions import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()   
        return jsonify({'message': str(e)}), 500   

    return jsonify({'message': 'User registered successfully'}), 201

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful', 'userId': user.userId}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from app import app, jwt, users_collection
from app.config import ADMKEY

@app.route("/api/v1/register", methods=["POST"])
def register():
    new_user = request.get_json()

    if 'role' not in new_user:
        return jsonify({'msg': 'Role is required in the request body'}), 400

    role = new_user['role']

    if role == 1:
        admkey = request.headers.get('AdmKey', None)
        if admkey == ADMKEY:
            new_user["role"] = 1
        else:
            return jsonify({'msg': 'Invalid admkey for admin registration'}), 401
    else:
        new_user["role"] = role

    hashed_password = generate_password_hash(new_user["password"], method='scrypt')
    new_user["password"] = hashed_password

    doc = users_collection.find_one({"username": new_user["username"]})
    if not doc:
        users_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409

@app.route("/api/v1/login", methods=["POST"])
def login():
    login_details = request.get_json()
    user_from_db = users_collection.find_one({'username': login_details['username']})

    if user_from_db and check_password_hash(user_from_db['password'], login_details['password']):
        access_token = create_access_token(identity=user_from_db['username'])
        refresh_token = create_refresh_token(identity=user_from_db['username'])
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return jsonify({'msg': 'The username or password is incorrect'}), 401

@app.route("/api/v1/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    refresh_token = create_refresh_token(identity=current_user)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route("/api/v1/user", methods=["GET"])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db:
        del user_from_db['_id'], user_from_db['password']
        return jsonify({'profile': user_from_db}), 200
    else:
        return jsonify({'msg': 'Profile not found'}), 404
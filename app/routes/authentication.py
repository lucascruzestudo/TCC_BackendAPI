from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from app import app, jwt, users_collection
from app.config import ADMKEY

jwt_redis_blocklist = set()

@app.route("/api/v1/register", methods=["POST"])
def register():
    new_user = request.get_json()

    if 'role' not in new_user:
        return jsonify({'msg': 'Role is required in the request body', 'success': False}), 400

    role = new_user['role']

    if role == 1:
        admkey = request.headers.get('AdmKey', None)
        if admkey == ADMKEY:
            new_user["role"] = 1
        else:
            return jsonify({'msg': 'Invalid admkey for admin registration', 'success': False}), 401
    else:
        new_user["role"] = role

    hashed_password = generate_password_hash(new_user["password"], method='scrypt')
    new_user["password"] = hashed_password

    new_user.setdefault("email", "")
    new_user.setdefault("profile_picture", "")
    new_user.setdefault("full_name", "")

    doc = users_collection.find_one({"username": new_user["username"]})
    if not doc:
        users_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully', 'success': True}), 201
    else:
        return jsonify({'msg': 'Username already exists', 'success': False}), 409

@app.route("/api/v1/login", methods=["POST"])
def login():
    login_details = request.get_json()
    user_from_db = users_collection.find_one({'username': login_details['username']})

    if user_from_db and check_password_hash(user_from_db['password'], login_details['password']):
        access_token = create_access_token(identity=user_from_db['username'])
        refresh_token = create_refresh_token(identity=user_from_db['username'])
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token, 'success': True}), 200

    return jsonify({'msg': 'The username or password is incorrect', 'success': False}), 401

@app.route("/api/v1/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    refresh_token = create_refresh_token(identity=current_user)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route("/api/v1/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    jwt_redis_blocklist.add(jti)
    return jsonify({'msg': 'Successfully logged out', 'success': True}), 200

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_redis_blocklist

import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from config import JWTKEY, ADMKEY, DEFAULT_ROLE, CONNECTION_STRING

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = JWTKEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)

client = MongoClient(CONNECTION_STRING)

db = client["labtcc"]
users_collection = db["users"]


@app.route("/api/v1/users", methods=["POST"])
def register():

    new_user = request.get_json()
    role = new_user.get('role', DEFAULT_ROLE)
    admkey = new_user.get('admkey', None)

    if role == 1:
        if admkey == ADMKEY:
            new_user["role"] = 1
        else:
            return jsonify({'msg': 'Invalid admkey for admin registration'}), 401
    else:
        new_user["role"] = role

    hashed_password = generate_password_hash(new_user["password"], method='sha256')
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
    return jsonify(access_token=access_token), 200

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

if __name__ == '__main__':
    app.run(debug=True)

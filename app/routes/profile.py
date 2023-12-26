from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, users_collection

@app.route("/api/v1/profile", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def manage_profile():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    
    if not user_from_db:
        return jsonify({'msg': 'Profile not found'}), 404

    if request.method == "GET":
        del user_from_db['_id'], user_from_db['password']
        return jsonify({'profile': user_from_db}), 200

    elif request.method == "PUT":
        update_data = request.get_json()

        if current_user != user_from_db['username']:
            return jsonify({'msg': 'Unauthorized to update this profile'}), 403

        if 'email' in update_data:
            user_from_db['email'] = update_data['email']

        if 'profile_picture' in update_data:
            user_from_db['profile_picture'] = update_data['profile_picture']

        users_collection.update_one({'username': current_user}, {'$set': user_from_db})

        return jsonify({'msg': 'Profile updated successfully'}), 200

    elif request.method == "DELETE":
        if user_from_db['role'] in [1, 2]:
            users_collection.delete_one({'username': current_user})
            return jsonify({'msg': 'User deleted successfully'}), 200
        else:
            return jsonify({'msg': 'Unauthorized to delete user'}), 403


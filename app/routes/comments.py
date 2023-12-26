from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import datetime
from app import app, projects_collection, users_collection
from app.functions import is_user_in_project

@app.route("/api/v1/manage_comments", methods=["POST", "DELETE"])
@jwt_required()
def manage_comments():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if user_from_db["role"] not in [3, 4]:
        return jsonify({'msg': 'Unauthorized to manage comments', 'success': False}), 403

    project_name = request.json.get("projectName")
    stage_id = int(request.json.get("stageId"))
    filename = request.json.get("filename")

    project = projects_collection.find_one({"projectName": project_name})
    if not project:
        return jsonify({'msg': 'Project not found', 'success': False}), 404

    if not is_user_in_project(str(user_from_db["_id"]), project):
        return jsonify({'msg': 'Unauthorized to manage comments for this project', 'success': False}), 403

    stage_index = stage_id - 1
    stage = project["stages"][stage_index]

    if not stage["active"]:
        return jsonify({'msg': 'Cannot manage comments in an inactive stage', 'success': False}), 400

    attachments = stage["attachments"]

    file_to_manage = None
    for attachment in attachments:
        if attachment["filename"] == filename:
            file_to_manage = attachment
            break

    if not file_to_manage:
        return jsonify({'msg': 'File not found in the specified stage', 'success': False}), 404

    if request.method == "POST":
        comment_text = request.json.get("comment")

        comment_data = {
            "user_id": str(user_from_db["_id"]),
            "username": user_from_db["username"],
            "comment_text": comment_text,
            "timestamp": datetime.datetime.now()
        }

        if "comments" not in file_to_manage:
            file_to_manage["comments"] = []

        file_to_manage["comments"].append(comment_data)

        project["lastUpdate"] = datetime.datetime.now()
        projects_collection.replace_one({"projectName": project_name}, project)

        return jsonify({'msg': 'Comment added successfully', 'success': True}), 200

    elif request.method == "DELETE":
        comment_id = request.json.get("commentId")

        if "comments" not in file_to_manage:
            return jsonify({'msg': 'No comments found for this file', 'success': False}), 404

        for comment in file_to_manage["comments"]:
            if comment["_id"] == comment_id:
                file_to_manage["comments"].remove(comment)

                project["lastUpdate"] = datetime.datetime.now()
                projects_collection.replace_one({"projectName": project_name}, project)

                return jsonify({'msg': 'Comment deleted successfully', 'success': True}), 200

        return jsonify({'msg': 'Comment not found for the specified file', 'success': False}), 404

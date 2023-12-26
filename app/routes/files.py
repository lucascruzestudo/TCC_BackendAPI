from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import os
from app import app, projects_collection, users_collection
import datetime
from werkzeug.utils import secure_filename
from app.config import ALLOWED_EXTENSIONS
from app.functions import allowed_file, is_user_in_project

@app.route("/api/v1/files", methods=["POST", "DELETE"])
@jwt_required()
def manage_files():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if user_from_db["role"] not in [3, 4]:
        return jsonify({'msg': 'Unauthorized to manage files', 'success': False}), 403

    project_name = request.form.get("projectName")
    stage_id = int(request.form.get("stageId"))
    file_action = request.method

    project = projects_collection.find_one({"projectName": project_name})
    if not project:
        return jsonify({'msg': 'Project not found', 'success': False}), 404

    if user_from_db["role"] == 4 and not is_user_in_project(str(user_from_db["_id"]), project):
        return jsonify({'msg': 'Unauthorized to manage files for this project', 'success': False}), 403

    if user_from_db["role"] == 3 and not is_user_in_project(str(user_from_db["_id"]), project):
        return jsonify({'msg': 'Unauthorized to manage files for this project', 'success': False}), 403

    stage_index = stage_id - 1
    stage = project["stages"][stage_index]
    attachments = stage["attachments"]

    if not stage["active"]:
        return jsonify({'msg': 'Cannot perform file action on inactive stage', 'success': False}), 400

    if file_action == "POST":
        file_title = request.form.get("title")

        if 'file' not in request.files:
            return jsonify({'msg': 'No file part', 'success': False}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'msg': 'No selected file', 'success': False}), 400

        if file and allowed_file(file.filename):
            project_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(project["_id"]))
            if not os.path.exists(project_folder_path):
                os.makedirs(project_folder_path)

            stage_folder_path = os.path.join(project_folder_path, f"stage_{stage_id}")
            if not os.path.exists(stage_folder_path):
                os.makedirs(stage_folder_path)

            existing_file_names = [attachment["filename"] for attachment in attachments]
            if file.filename in existing_file_names:
                return jsonify({'msg': 'File with the same name already exists in the stage', 'success': False}), 400

            filename = secure_filename(file.filename)
            file_path = os.path.join(stage_folder_path, filename)

            if os.path.exists(file_path):
                return jsonify({'msg': 'File with the same name already exists on the server', 'success': False}), 400

            file.save(file_path)

            attachments.append({
            "title": file_title,
            "filename": filename,
            "file_path": file_path,
            "status": 0
            })

            project["lastUpdate"] = datetime.datetime.now()
            projects_collection.replace_one({"projectName": project_name}, project)

            return jsonify({'msg': 'File uploaded successfully', 'success': True}), 200

        return jsonify({'msg': 'Invalid file type', 'success': False}), 400

    elif file_action == "DELETE":
        file_name = request.form.get("fileName")

        for attachment in attachments:
            if attachment["filename"] == file_name:
                if not stage["active"]:
                    return jsonify({'msg': 'Cannot delete file from inactive stage', 'success': False}), 400

                if user_from_db["role"] == 3:
                    return jsonify({'msg': 'Advisors are not allowed to delete files', 'success': False}), 403

                os.remove(os.path.join(attachment["file_path"], file_name))

                attachments.remove(attachment)

                project["lastUpdate"] = datetime.datetime.now()
                projects_collection.replace_one({"projectName": project_name}, project)

                return jsonify({'msg': 'File deleted successfully', 'success': True}), 200

        return jsonify({'msg': 'File not found in the specified stage', 'success': False}), 404
    
@app.route("/api/v1/manage_file_status", methods=["POST"])
@jwt_required()
def manage_file_status():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if user_from_db["role"] != 3:
        return jsonify({'msg': 'Unauthorized to update file status', 'success': False}), 403

    project_name = request.json.get("projectName")
    stage_id = int(request.json.get("stageId"))
    filename = request.json.get("filename")
    new_status = int(request.json.get("newStatus"))

    project = projects_collection.find_one({"projectName": project_name})
    if not project:
        return jsonify({'msg': 'Project not found', 'success': False}), 404

    if not is_user_in_project(str(user_from_db["_id"]), project):
        return jsonify({'msg': 'Unauthorized to update file status for this project', 'success': False}), 403

    if user_from_db["role"] == 3 and str(user_from_db["_id"]) != str(project["advisor"]["advisorId"]):
        return jsonify({'msg': 'Unauthorized to update file status. Not the advisor of this project', 'success': False}), 403

    stage_index = stage_id - 1
    stage = project["stages"][stage_index]
    
    if not stage["active"]:
        return jsonify({'msg': 'Cannot update file status in an inactive stage', 'success': False}), 400

    attachments = stage["attachments"]

    file_to_update = None
    for attachment in attachments:
        if attachment["filename"] == filename:
            file_to_update = attachment
            break

    if not file_to_update:
        return jsonify({'msg': 'File not found in the specified stage', 'success': False}), 404

    if new_status in (1,2):
        file_to_update["status"] = new_status
        project["lastUpdate"] = datetime.datetime.now()
        projects_collection.replace_one({"projectName": project_name}, project)

        return jsonify({'msg': 'File status updated successfully', 'success': True}), 200
    else:
        return jsonify({'msg': 'Invalid status value. Must be 1 (approved), or 2 (rejected)', 'success': False}), 400
    
@app.route("/api/v1/files", methods=["GET"])
@jwt_required()
def get_stage_files():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if not user_from_db:
        return jsonify({'msg': 'User not found', 'success': False}), 404

    if user_from_db["role"] not in [2, 3]:
        return jsonify({'msg': 'Unauthorized to get stage files', 'success': False}), 403

    project_name = request.args.get("projectName")
    stage_id = request.args.get("stageId")

    if not project_name:
        return jsonify({'msg': 'Project Name is required', 'success': False}), 400

    if not stage_id:
        return jsonify({'msg': 'Stage ID is required', 'success': False}), 400

    try:
        stage_id = int(stage_id)
    except ValueError:
        return jsonify({'msg': 'Invalid stage ID format', 'success': False}), 400

    project = projects_collection.find_one({"projectName": project_name})
    if not project:
        return jsonify({'msg': 'Project not found', 'success': False}), 404

    if not is_user_in_project(str(user_from_db["_id"]), project):
        return jsonify({'msg': 'Unauthorized to get files for this project', 'success': False}), 403

    if stage_id <= 0 or stage_id > len(project["stages"]):
        return jsonify({'msg': 'Invalid stage ID', 'success': False}), 400

    stage_index = stage_id - 1
    stage = project["stages"][stage_index]

    attachments = stage.get("attachments", [])
    
    if not attachments:
        return jsonify({'msg': 'No files available for this stage', 'success': True, 'files': []}), 200

    files_with_comments = []

    for attachment in attachments:
        file_info = {
            "title": attachment.get("title", ""),
            "filename": attachment.get("filename", ""),
            "status": attachment.get("status", 0),
            "comments": []
        }

        if "comments" in attachment:
            comments_data = []
            for comment in attachment["comments"]:
                comments_data.append({
                    "_id": str(comment["_id"]),
                    "user_id": comment["user_id"],
                    "username": comment["username"],
                    "comment_text": comment["comment_text"],
                    "timestamp": comment["timestamp"]
                })
            file_info["comments"] = comments_data

        files_with_comments.append(file_info)

    return jsonify({'files': files_with_comments, 'success': True}), 200
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, projects_collection, users_collection
import datetime


@app.route("/api/v1/stages/approve", methods=["POST"])
@jwt_required()
def approve_stage():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if not user_from_db or user_from_db["role"] != 3:
        return jsonify({'msg': 'Unauthorized to approve stages', 'success': False}), 403

    try:
        project = projects_collection.find_one({"advisor.advisorId": str(user_from_db["_id"])})

        if not project:
            return jsonify({'msg': 'Project not found or you are not the advisor for any project', 'success': False}), 404

        current_stage_id = project.get("currentStage", 0)

        if current_stage_id == 0:
            return jsonify({'msg': 'Cannot approve further stages, project is already completed', 'success': False}), 400

        current_stage_index = current_stage_id - 1

        if current_stage_index < len(project["stages"]):
            current_stage = project["stages"][current_stage_index]
            current_stage["active"] = False
            current_stage["completed"] = True
            current_stage["startDate"] = datetime.datetime.now()

            if current_stage_id < 5:
                next_stage_index = current_stage_index + 1
                next_stage = project["stages"][next_stage_index]
                next_stage["active"] = True
                project["currentStage"] = next_stage["stageId"]
                next_stage["startDate"] = datetime.datetime.now()

            else:
                project["currentStage"] = 0
                project["completed"] = True
                project["active"] = False

            project["lastUpdate"] = datetime.datetime.now()

            projects_collection.replace_one({"advisor.advisorId": str(user_from_db["_id"])}, project)

            return jsonify({'msg': 'Stage approved successfully', 'success': True}), 200
        else:
            return jsonify({'msg': 'Invalid current stage ID or the stage is not found in the project', 'success': False}), 400

    except Exception as e:
        return jsonify({'msg': f'Error approving stage: {str(e)}', 'success': False}), 500
    
@app.route("/api/v1/stages/revert", methods=["POST"])
@jwt_required()
def revert_stage():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if not user_from_db or user_from_db["role"] != 3:
        return jsonify({'msg': 'Unauthorized to revert stages', 'success': False}), 403

    try:
        data = request.get_json()
        project_name = data.get("projectName")

        if not project_name:
            return jsonify({'msg': 'Invalid request body', 'success': False}), 400

        project = projects_collection.find_one({"projectName": project_name, "advisor.advisorId": str(user_from_db["_id"])})

        if not project:
            return jsonify({'msg': 'Project not found or you are not the advisor for this project', 'success': False}), 404

        current_stage_id = project.get("currentStage", 0)

        if current_stage_id == 0:
            project["currentStage"] = 5
            project["completed"] = False
            project["active"] = True

            stage_5 = project["stages"][4]
            stage_5["active"] = True
            stage_5["completed"] = False
            stage_5["startDate"] = datetime.datetime.now()

        elif 1 < current_stage_id <= 5:
            current_stage_index = current_stage_id - 1
            current_stage = project["stages"][current_stage_index]

            current_stage["active"] = False
            current_stage["completed"] = False
            current_stage["startDate"] = None

            previous_stage_index = current_stage_index - 1
            previous_stage = project["stages"][previous_stage_index]

            project["currentStage"] = previous_stage["stageId"]
            previous_stage["active"] = True
            previous_stage["completed"] = False
            previous_stage["startDate"] = datetime.datetime.now()
            previous_stage["dueDate"] = None

        elif current_stage_id == 1:
            return jsonify({'msg': 'Cannot revert stage 1', 'success': False}), 400

        else:
            return jsonify({'msg': 'Invalid stage ID', 'success': False}), 400

        project["lastUpdate"] = datetime.datetime.now()

        projects_collection.replace_one({"projectName": project_name}, project)

        return jsonify({'msg': 'Stage reverted successfully', 'success': True}), 200

    except Exception as e:
        return jsonify({'msg': f'Error reverting stage: {str(e)}', 'success': False}), 500 

from datetime import datetime

@app.route("/api/v1/stages/setDueDate", methods=["POST"])
@jwt_required()
def set_due_date():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if not user_from_db or user_from_db["role"] != 3:
        return jsonify({'msg': 'Unauthorized to set due date', 'success': False}), 403

    try:
        data = request.get_json()
        project_name = data.get("projectName")
        due_date_str = data.get("dueDate")

        if not project_name or not due_date_str:
            return jsonify({'msg': 'Invalid request body', 'success': False}), 400

        project = projects_collection.find_one({"projectName": project_name, "advisor.advisorId": str(user_from_db["_id"])})

        if not project:
            return jsonify({'msg': 'Project not found or you are not the advisor for this project', 'success': False}), 404

        current_stage_id = project.get("currentStage", 0)

        if current_stage_id == 0:
            return jsonify({'msg': 'Cannot set due date, project is already completed', 'success': False}), 400

        current_stage_index = current_stage_id - 1

        if current_stage_index < len(project["stages"]):
            current_stage = project["stages"][current_stage_index]
            current_stage["dueDate"] = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%S")

            project["lastUpdate"] = datetime.now()

            projects_collection.replace_one({"projectName": project_name}, project)

            return jsonify({'msg': 'Due date set successfully', 'success': True}), 200
        else:
            return jsonify({'msg': 'Invalid current stage ID or the stage is not found in the project', 'success': False}), 400

    except Exception as e:
        return jsonify({'msg': f'Error setting due date: {str(e)}', 'success': False}), 500

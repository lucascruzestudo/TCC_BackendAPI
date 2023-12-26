from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from app import app, projects_collection, users_collection
import datetime

def is_user_in_project(user_id, project):
    advisor_id = str(project["advisor"]["advisorId"]) if project["advisor"] else None
    student_ids = [str(s["studentId"]) for s in project["students"]] if project["students"] else []

    return user_id in student_ids or user_id == advisor_id

@app.route("/api/v1/manage_projects", methods=["POST"])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    
    if user_from_db["role"] in [1, 2]:
        projectName = request.get_json().get("projectName")

        if projectName is None or projectName == "":
            return jsonify({'msg': 'Project name cannot be null or empty'}), 400

        existing_project = projects_collection.find_one({"projectName": projectName})
        if existing_project:
            return jsonify({'msg': 'Project with the same name already exists'}), 400

        new_project = {
            "projectName": projectName,
            "active": True,
            "students": [],
            "advisor": {},
            "startDate": datetime.datetime.now(),
            "dueDate": None,
            "stages": [
                {
                    "stageId": 1,
                    "stageName": "Ficha de Inscrição",
                    "attachments": [],
                    "startDate": datetime.datetime.now(),
                    "dueDate": None,
                    "active": True
                },
                {
                    "stageId": 2,
                    "stageName": "Pré-Projeto",
                    "attachments": [],
                    "startDate": None,
                    "dueDate": None,
                    "active": False
                },
                {
                    "stageId": 3,
                    "stageName": "Relatório Parcial",
                    "attachments": [],
                    "startDate": None,
                    "dueDate": None,
                    "active": False
                },
                {
                    "stageId": 4,
                    "stageName": "Entrega Do Projeto",
                    "attachments": [],
                    "startDate": None,
                    "dueDate": None,
                    "active": False
                },
                {
                    "stageId": 5,
                    "stageName": "Entrega Revisada do Projeto",
                    "attachments": [],
                    "startDate": None,
                    "dueDate": None,
                    "active": False
                },
                
            ],
            "lastUpdate": datetime.datetime.now()
        }
        
        projects_collection.insert_one(new_project)
        return jsonify({'msg': 'Project created successfully'}), 201
    else:
        return jsonify({'msg': 'Unauthorized to create project'}), 403

@app.route("/api/v1/manage_students", methods=["POST", "DELETE"])
@jwt_required()
def manage_students():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if user_from_db["role"] not in [1, 2, 3]:
        return jsonify({'msg': 'Unauthorized to manage students', 'success': False}), 403

    project_name = request.get_json().get("projectName")
    usernames = request.get_json().get("students")

    if project_name is None or project_name == "" or usernames is None:
        return jsonify({'msg': 'Invalid request body', 'success': False}), 400

    project = projects_collection.find_one({"projectName": project_name})

    if not project:
        return jsonify({'msg': 'Project not found', 'success': False}), 404

    existing_students = {str(s["studentId"]): s["studentName"] for s in project["students"]}

    student_info = []
    for username in usernames:
        user_doc = users_collection.find_one({"username": username, "role": 4})
        if not user_doc:
            return jsonify({'msg': f'User "{username}" not found or is not a valid student', 'success': False}), 400
        student_info.append({"studentId": str(user_doc["_id"]), "studentName": user_doc["username"]})

    if request.method == "POST":
        for student in student_info:
            if student["studentId"] in existing_students:
                return jsonify({'msg': f'User "{student["studentName"]}" already has a project', 'success': False}), 400

        project["students"].extend(student_info)

    elif request.method == "DELETE":
        for student in student_info:
            if str(student["studentId"]) not in existing_students:
                return jsonify({'msg': f'User "{student["studentName"]}" is not part of this project', 'success': False}), 400

        project["students"] = [s for s in project["students"] if str(s["studentId"]) not in [str(student["studentId"]) for student in student_info]]

    project["lastUpdate"] = datetime.datetime.now()

    projects_collection.replace_one({"projectName": project_name}, project)

    response = {
        'msg': 'Students managed successfully',
        'project_name': project_name,
        'students': [{"studentId": s["studentId"], "studentName": s["studentName"]} for s in project["students"]],
        'success': True
    }

    return jsonify(response), 200

@app.route("/api/v1/manage_advisor", methods=["POST", "DELETE"])
@jwt_required()
def manage_advisor():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if user_from_db["role"] not in [1, 2]:
        return jsonify({'msg': 'Unauthorized to manage advisor', 'success': False}), 403

    project_name = request.get_json().get("projectName")
    advisor_username = request.get_json().get("advisor")

    if project_name is None or project_name == "" or advisor_username is None:
        return jsonify({'msg': 'Invalid request body', 'success': False}), 400

    project = projects_collection.find_one({"projectName": project_name})

    if not project:
        return jsonify({'msg': 'Project not found', 'success': False}), 404

    advisor_info = {}
    advisor_doc = users_collection.find_one({"username": advisor_username, "role": 3})
    if not advisor_doc:
        return jsonify({'msg': f'User "{advisor_username}" not found or is not a valid advisor', 'success': False}), 400
    advisor_info["advisorId"] = str(advisor_doc["_id"])
    advisor_info["advisorName"] = advisor_doc["username"]

    if request.method == "POST":
        if "advisor" in project and project["advisor"]:
            current_advisor_id = project["advisor"]["advisorId"]
            if current_advisor_id == advisor_info["advisorId"]:
                return jsonify({'msg': f'The specified advisor is already the advisor for the project', 'success': False}), 400

            return jsonify({'msg': f'The project already has an advisor', 'success': False}), 400

        project["advisor"] = advisor_info

    elif request.method == "DELETE":
        if "advisor" not in project or project["advisor"]["advisorId"] != advisor_info["advisorId"]:
            return jsonify({'msg': f'The project does not have the specified advisor', 'success': False}), 400

        project["advisor"] = None

    project["lastUpdate"] = datetime.datetime.now()

    projects_collection.replace_one({"projectName": project_name}, project)

    response = {
        'msg': 'Advisor managed successfully',
        'project_name': project_name,
        'advisor': project.get("advisor", {}),
        'success': True
    }

    return jsonify(response), 200

@app.route("/api/v1/get_projects", methods=["GET"])
@jwt_required()
def get_projects():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if not user_from_db:
        return jsonify({'msg': 'User not found', 'success': False}), 404

    role = user_from_db["role"]

    try:
        if role > 0 and role <= 2:
            projects = list(projects_collection.find({}, {"_id": 0}))
        elif role == 3:
            advisor_projects = list(projects_collection.find({"advisor.advisorId": str(user_from_db["_id"])}, {"_id": 0}))
            if not advisor_projects:
                return jsonify({'msg': 'You are not assigned to any projects as an advisor', 'success': True, 'projects': []}), 200
            projects = advisor_projects
        elif role == 4:
            student_projects = list(projects_collection.find({"students.studentId": str(user_from_db["_id"])}, {"_id": 0}))
            if not student_projects:
                return jsonify({'msg': 'You do not have a project assigned', 'success': True, 'projects': []}), 200
            projects = student_projects
        else:
            return jsonify({'msg': 'Invalid user role', 'success': False}), 403

        return jsonify({'msg': 'Projects retrieved successfully', 'success': True, 'projects': projects}), 200
    except Exception as e:
        return jsonify({'msg': f'Error retrieving projects: {str(e)}', 'success': False}), 500
    

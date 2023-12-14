import datetime
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from werkzeug.utils import secure_filename
from config import JWTKEY, ADMKEY, DEFAULT_ROLE, CONNECTION_STRING

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = JWTKEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)

client = MongoClient(CONNECTION_STRING)

db = client["labtcc"]
users_collection = db["users"]
projects_collection = db["projects"]

UPLOAD_FOLDER = 'tmp/files'
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'py' ,'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route("/api/v1/projects", methods=["GET"])
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
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_user_in_project(user_id, project):
    advisor_id = str(project["advisor"]["advisorId"]) if project["advisor"] else None
    student_ids = [str(s["studentId"]) for s in project["students"]] if project["students"] else []

    return user_id in student_ids or user_id == advisor_id

@app.route("/api/v1/manage_files", methods=["POST", "DELETE"])
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

if __name__ == '__main__':
    app.run(debug=True)
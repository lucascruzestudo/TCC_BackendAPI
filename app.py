import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
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

@app.route("/api/v1/register", methods=["POST"])
def register():
    new_user = request.get_json()
    role = new_user.get('role', DEFAULT_ROLE)

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
        print(user_from_db['password'])
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
                    "stageName": "pre-projeto",
                    "attachments": [],
                    "startDate": datetime.datetime.now(),
                    "dueDate": None,
                    "active": True
                },
                {
                    "stageId": 2,
                    "stageName": "desenvolvimento",
                    "attachments": [],
                    "startDate": None,
                    "dueDate": None,
                    "active": False
                },
                {
                    "stageId": 3,
                    "stageName": "documentação",
                    "attachments": [],
                    "startDate": None,
                    "dueDate": None,
                    "active": False
                }
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

if __name__ == '__main__':
    app.run(debug=True)
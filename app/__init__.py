import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from app.config import CONNECTION_STRING, JWTKEY

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
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'py', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app.routes import authentication, projects, files, comments

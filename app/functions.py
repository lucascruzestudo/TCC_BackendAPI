from app.config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_user_in_project(user_id, project):
    advisor_id = str(project["advisor"]["advisorId"]) if project["advisor"] else None
    student_ids = [str(s["studentId"]) for s in project["students"]] if project["students"] else []

    return user_id in student_ids or user_id == advisor_id
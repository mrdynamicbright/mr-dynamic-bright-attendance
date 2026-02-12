import os
import io
import base64
import numpy as np
import face_recognition
import pandas as pd

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime

from models import db, Employee, Location, Attendance
from utils import is_within_radius, calculate_status
from analytics import today_summary

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix postgres url issue (Render fix)
if app.config['SQLALCHEMY_DATABASE_URI'] and \
   app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        app.config['SQLALCHEMY_DATABASE_URI'].replace(
            "postgres://", "postgresql://", 1
        )

db.init_app(app)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- FACE MATCH ----------------

def match_face(encoding):
    employees = Employee.query.all()
    for emp in employees:
        if face_recognition.compare_faces([emp.face_encoding], encoding)[0]:
            return emp
    return None

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/attendance", methods=["POST"])
def attendance():
    data = request.json

    photo = base64.b64decode(data["photo"].split(",")[1])
    user_lat, user_lon = map(float, data["gps"].split(","))
    check_type = data["type"]

    image = face_recognition.load_image_file(io.BytesIO(photo))
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        return jsonify({"error": "No face detected"})

    emp = match_face(encodings[0])
    if not emp:
        return jsonify({"error": "Face not recognized"})

    location = Location.query.get(emp.location_id)

    if not is_within_radius(user_lat, user_lon, location):
        return jsonify({"error": "Outside allowed area"})

    record = Attendance.query.filter_by(
        employee_id=emp.id,
        check_out=None
    ).first()

    if check_type == "IN":
        new = Attendance(
            employee_id=emp.id,
            location_name=location.name,
            check_in=datetime.now(),
            gps_location=data["gps"]
        )
        db.session.add(new)
        db.session.commit()
        return jsonify({"success": f"Check-In Successful {emp.name}"})

    if record:
        record.check_out = datetime.now()
        hours = (record.check_out - record.check_in).total_seconds() / 3600
        record.work_hours = hours
        record.status = calculate_status(hours)
        db.session.commit()
        return jsonify({"success": f"Check-Out Successful {emp.name}"})

    return jsonify({"error": "No check-in found"})

# ---------------- AUTO ABSENT ----------------

@app.route("/mark_absent")
def mark_absent():
    today = datetime.now().date()
    employees = Employee.query.all()

    for emp in employees:
        exists = Attendance.query.filter(
            Attendance.employee_id == emp.id,
            Attendance.check_in != None
        ).first()

        if not exists:
            absent = Attendance(
                employee_id=emp.id,
                location_name="N/A",
                check_in=datetime.now(),
                work_hours=0,
                status="Absent"
            )
            db.session.add(absent)

    db.session.commit()
    return "Absent Marked"

# ---------------- DASHBOARD ----------------

@app.route("/admin")
def admin():
    total, present, half, absent = today_summary()
    records = Attendance.query.order_by(Attendance.check_in.desc()).all()

    return render_template(
        "admin.html",
        total=total,
        present=present,
        half=half,
        absent=absent,
        records=records
    )

# ---------------- EXPORT ----------------

@app.route("/export")
def export():
    records = Attendance.query.all()

    data = [{
        "Employee ID": r.employee_id,
        "Location": r.location_name,
        "Check In": r.check_in,
        "Check Out": r.check_out,
        "Hours": r.work_hours,
        "Status": r.status
    } for r in records]

    df = pd.DataFrame(data)
    file = "attendance.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)

# ---------------- INIT ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

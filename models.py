from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    radius = db.Column(db.Integer, default=200)


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    location_name = db.Column(db.String(100))
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    work_hours = db.Column(db.Float)
    status = db.Column(db.String(20))
    gps_location = db.Column(db.String(200))

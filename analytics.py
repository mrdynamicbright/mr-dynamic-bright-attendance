from models import Attendance
from sqlalchemy import func
from datetime import datetime

def today_summary():
    today = datetime.now().date()

    total = Attendance.query.filter(
        func.date(Attendance.check_in) == today
    ).count()

    present = Attendance.query.filter(
        Attendance.status == "Present",
        func.date(Attendance.check_in) == today
    ).count()

    half = Attendance.query.filter(
        Attendance.status == "Half-Day",
        func.date(Attendance.check_in) == today
    ).count()

    absent = Attendance.query.filter(
        Attendance.status == "Absent",
        func.date(Attendance.check_in) == today
    ).count()

    return total, present, half, absent

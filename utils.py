from math import radians, sin, cos, sqrt, atan2

def is_within_radius(user_lat, user_lon, location):
    R = 6371000

    dlat = radians(location.latitude - user_lat)
    dlon = radians(location.longitude - user_lon)

    a = sin(dlat/2)**2 + cos(radians(user_lat)) * \
        cos(radians(location.latitude)) * sin(dlon/2)**2

    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c <= location.radius

def calculate_status(hours):
    if hours >= 6:
        return "Present"
    elif 0 < hours < 6:
        return "Half-Day"
    else:
        return "Absent"

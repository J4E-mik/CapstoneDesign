from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # m
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def is_within_radius(current: tuple, target: tuple, radius_m: float = 5.0) -> bool:
    return haversine(current[0], current[1], target[0], target[1]) <= radius_m

def is_within_step(current_lat, current_lon, step_lat, step_lon, radius=5.0):
    return haversine(current_lat, current_lon, step_lat, step_lon) <= radius
from schemas.schemas import GPSUpdateResponse, GPSTrackResponse
from services.session import user_locations, user_session
from utils.gps_tracker import is_within_radius, is_within_step

class GPSService:
    def update_user_location(self, user_id: str, lat: float, lon: float):
        print(f"[DEBUG] Received GPS update from {user_id}: ({lat}, {lon})")
        user_locations[user_id] = (lon, lat)
        return GPSUpdateResponse(user=user_id, message="GPS updated")
    
    def track_user_route(self, user_id: str, lat: float, lon: float):
        if user_id not in user_session:
            return GPSTrackResponse(error="No active session found.")
        
        session = user_session[user_id]
        itinerary = session["itinerary"]
        current_leg_idx = session.get("current_leg_idx", 0)
        legs = itinerary["legs"]

        if current_leg_idx >= len(legs):
            return GPSTrackResponse(message="Route complete.")
        
        current_leg = legs[current_leg_idx]
        mode = current_leg["mode"]
        end_point = current_leg["end"]

        if is_within_radius((lat, lon), (end_point["lat"], end_point["lon"])):
            session["current_leg_idx"] += 1
            session["current_step_idx"] = 0
            return GPSTrackResponse(message=f"{mode} 완료, 다음 모드로 진행 필요")

        if mode == "WALK":
            steps = current_leg["steps"]
            step_idx = session.get("current_step_idx", 0)

            if step_idx >= len(steps):
                session["current_leg_idx"] += 1
                session["current_step_idx"] = 0
                return GPSTrackResponse(message="Walk segment complete. proceed to next.")
            
            step = steps[step_idx]
            linestring = step["linestring"].split()
            step_end_lon, step_end_lat = map(float, linestring[-1].split(','))

            if is_within_step(lat, lon, step_end_lat, step_end_lon):
                session["current_step_idx"] += 1
                return GPSTrackResponse(message=f"Reached step: {step['text']}")
            
            return GPSTrackResponse(message=f"Proceeding to step: {step['text']}")
        
        elif mode in ["BUS", "SUBWAY"]:
            pass_stations = current_leg["passStopList"]["stationList"]
            boarding_stop = pass_stations[0]["stationName"]
            alighting_stop = pass_stations[-1]["stationName"]
            route_number = current_leg["route"]

            return GPSTrackResponse(
                message = f"{mode} 이용: {route_number}",
                bus_number=route_number if mode == "BUS" else None,
                line_number=route_number if mode == "SUBWAY" else None,
                stop_count=len(pass_stations),
                boarding_stop=boarding_stop if mode == "BUS" else None,
                alighting_stop=alighting_stop if mode == "BUS" else None,
                boarding_station=boarding_stop if mode == "SUBWAY" else None,
                alighting_station=alighting_stop if mode == "SUBWAY" else None
            )
    
        return GPSTrackResponse(error="Unsupported mode.")
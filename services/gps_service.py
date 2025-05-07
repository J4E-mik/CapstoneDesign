from schemas.schemas import GPSUpdateResponse, GPSTrackResponse
from services.routing_service import RoutingService
from services.session import user_locations, user_session
from utils.gps_tracker import is_within_radius, is_within_step

class GPSService:
    def update_user_location(self, user_id: str, lat: float, lon: float):
        user_locations[user_id] = (lon, lat)
        return GPSUpdateResponse(user=user_id, message="GPS updated")
    
    def track_user_route(self, user_id: str, lat: float, lon: float):
        if user_id not in user_session:
            return GPSTrackResponse(error="No active session found.")
        
        session = user_session[user_id]
        itinerary = session["itinerary"]
        current_leg_idx = session.get("current_leg_idx", 0)
        legs = itinerary.get("legs", [])

        if current_leg_idx >= len(legs):
            return GPSTrackResponse(message="Route complete.")
        
        current_leg = legs[current_leg_idx]
        mode = current_leg.get("mode")

        if mode == "WALK":
            steps = session["walk_steps"]
            step_idx = session.get("current_step_idx", 0)

            if step_idx >= len(steps):
                session["current_leg_idx"] += 1
                session["current_step_idx"] = 0
                return GPSTrackResponse(message="Walk segment complete. proceed to next.")
            
            step = steps[step_idx]
            if is_within_step(lat, lon, step["lat"], step["lon"]):
                session["current_step_idx"] += 1
                return GPSTrackResponse(message=f"Reached step: {step['text']}")
            
            return GPSTrackResponse(message=f"Proceeding to step: {step['text']}")
        
        elif mode in ["BUS", "SUBWAY"]:
            target = current_leg["end"]
            if is_within_radius((lat,lon), (target["lat"], target["lon"])):
                session["current_leg_idx"] += 1
                session["current_step_idx"] = 0
                return GPSTrackResponse(message=f"{mode} segment complet, proceed next.")
            return GPSTrackResponse(message=f"{mode} segment ongoing...") 
    
        return GPSTrackResponse(error="Unsupported mode.")
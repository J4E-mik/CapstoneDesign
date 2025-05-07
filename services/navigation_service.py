from config import settings
from schemas.schemas import RouteResponse
import requests

class NavigationService:
    def __init__(self):
        self.tmap_key = settings.TMAP_APP_KEY
        self.poi_url = "https://apis.openapi.sk.com/tmap/pois"
        self.transit_url = "https://apis.openapi.sk.com/transit/routes"

    def get_coordinates_by_keyword(self, keyword: str):
        paramas = {
            "version" : 1,
            "appKey" : self.tmap_key,
            "searchKeyword" : keyword
        }
        response = requests.get(self.poi_url, params=paramas)
        if response.ok:
            pois = response.json().get("searchPoiInfo",{}).get("pois",{}).get("poi", [])
            if pois:
                return float(pois[0]["frontLon"]), float(pois[0]["frontLat"])
        return None, None
    
    def get_transit_route(self, start, end):
        payload = {
            "startX": start[0],
            "startY": start[1],
            "endX": end[0],
            "endY": end[1],
            "format": "json"
        }
        headers = {"appKey": self.tmap_key}
        response = requests.post(self.transit_url, json=payload, headers=headers)
        if response.ok:
            return response.json()
        return None
    
    def get_route(self, user_lon, user_lat, destination) -> RouteResponse:
        dest_coords = self.get_coordinates_by_keyword(destination)
        if not all(dest_coords):
            return {"error": "Destination Not Found."}
        
        route = self.get_transit_route((user_lon, user_lat), dest_coords)
        if not route:
            return {"error": "Route Not Found."}
        
        itinerary = route["metaData"]["plan"]["itineraries"][1]

        return RouteResponse(
            destination = destination,
            start = {"lat":user_lat, "lon":user_lon},
            end = {"lat":dest_coords[1], "lon":dest_coords[0]},
            itinerary=itinerary
        )
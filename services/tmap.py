# TMAP_TRANSIT, POI API등
import requests, os
from dotenv import load_dotenv

load_dotenv()
TMAP_APP_KEY = os.getenv("TMAP_APP_KEY")

def get_coordinates_by_keyword(keyword: str):
    TMAP_POI_URL = "https://apis.openapi.sk.com/tmap/pois"
    params = {
        "version": 1,
        "appKey": TMAP_APP_KEY,
        "searchKeyword": keyword
    }
    response = requests.get(TMAP_POI_URL, params=params)
    if response.status_code == 200:
        pois = response.json()["searchPoiInfo"]["pos"]["poi"]
        if pois:
            return pois[0]["frontLon"], pois[0]["frontLat"]
    return None, None

def get_transit_route(start_coord: tuple, end_coord: tuple):
    TMAP_TRANSIT_URL = "https://apis.openapi.sk.com/transit/routes"
    payload = {
        "startX": start_coord[0],
        "startY": start_coord[1],
        "endX": end_coord[0],
        "endY": end_coord[1],
        "lang": 0,
        "format": "json",
        "count": 10
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "appKey": TMAP_APP_KEY
    }
    response = requests.post(TMAP_TRANSIT_URL, json=payload, headers=headers)
    return response.json() if response.status_code == 200 else None
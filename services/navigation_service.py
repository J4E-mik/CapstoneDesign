from config import settings
from schemas.schemas import RouteResponse
from services.session import user_session
import requests, json

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
    
    def get_walk_score(self, legs):
        score = 0
        for leg in legs:
            if leg['mode'] == 'WALK':
                time = leg.get('sectionTime', 0)
                dist = leg.get('distance', 0)
                steps = len(leg.get('steps', [])) if leg.get('steps') else 1
                score += time *0.5 + dist *0.3 + steps * 0.2
        return score
    
    def get_bus_score(self, legs):
        score = 0
        for leg in legs:
            if leg['mode'] == 'BUS':
                time = leg.get('sectionTime', 0)
                dist = leg.get('distance', 0)
                stops = len(leg.get('passStopList', {}).get('stationList',[]))
                score += time * 0.5 + dist * 0.2 + stops * 0.3
        return score
    
    def get_subway_score(self, legs):
        score = 0
        for leg in legs:
            if leg['mode'] == 'SUBWAY':
                time = leg.get('sectionTime', 0)
                dist = leg.get('distance', 0)
                stops = len(leg.get('passStopList', {}).get('stationList',[]))
                score += time * 0.4 + dist * 0.3 + stops * 0.3
        return score
    
    def get_total_score(self, itinerary):
        total_time = itinerary.get('totalTime', 0)
        transfer_count = itinerary.get('transferCount', 0)
        legs = itinerary.get('legs', [])

        walk_score = self.get_walk_score(legs)
        bus_score = self.get_bus_score(legs)
        subway_score = self.get_subway_score(legs)

        score = total_time * 0.3 + transfer_count * 10 + walk_score + bus_score + subway_score
        return score
    
    def select_best_itinerary(self, itineraries):
        scored = [(self.get_total_score(it), it) for it in itineraries]
        scored.sort(key=lambda x: x[0])
        return scored[0][1]
    
    def get_score_breakdown(self, itineraries):
        result = []
        for idx, it in enumerate(itineraries):
            walk_score = self.get_walk_score(it["legs"])
            bus_score = self.get_bus_score(it["legs"])
            subway_score = self.get_subway_score(it["legs"])
            total_score = self.get_total_score(it)
            transfer_count = it.get('transferCount', 0)
            result.append({
                "index":idx,
                "total_score": total_score,
                "walk_score": walk_score,
                "bus_score": bus_score,
                "subway_score": subway_score,
                "transfer_count": transfer_count
            })
            
        return result

    def get_route(self, user_id, user_lon, user_lat, destination) -> RouteResponse:
        '''
        실제 서비스 로직
        API요청 -> 경로 지수 계산 -> 최적경로 선택 -> 사용자 경로 전송
        '''
        dest_coords = self.get_coordinates_by_keyword(destination)
        if not all(dest_coords):
            return {"error": "Destination Not Found."}
        
        route = self.get_transit_route((user_lon, user_lat), dest_coords)
        if not route:
            return {"error": "Route Not Found."}
        
        itineraries = route["metaData"]["plan"]["itineraries"]

        itinerary = self.select_best_itinerary(itineraries)

        user_session[user_id] = {
            "itineraries": itineraries,
            "itinerary": itinerary,
            "current_leg_idx": 0,
            "current_step_idx": 0
        }

        return RouteResponse(
            destination = destination,
            start = {"lat":user_lat, "lon":user_lon},
            end = {"lat":dest_coords[1], "lon":dest_coords[0]},
            itinerary=itinerary
        )
    
    def get_route_file(self, user_id, user_lon, user_lat, destination) -> RouteResponse:
        '''
        시연 영상을 위해 고정 된 경로를 선택 반환하는 함수
        API응답을 json으로 저장해둔 파일에서 사전에 선정한 경로를 불러옴
        '''
        with open("data/transit_response_road.json", "r", encoding='utf-8') as f:
            route_data = json.load(f)

        itineraries = route_data.get("metaData", {}).get("plan", {}).get("itineraries", [])
        if not itineraries:
            return {"error": "경로 데이터 없음."}
        
        itinerary = itineraries[1]

        user_session[user_id] = {
            "itineraries": itineraries,
            "itinerary": itinerary,
            "current_leg_idx": 0,
            "current_step_idx": 0
        }

        return RouteResponse(
            destination = destination,
            start = {"lat":user_lat, "lon":user_lon},
            end = {"lat":itinerary["legs"][-1]["end"]["lat"],
                   "lon":itinerary["legs"][-1]["end"]["lon"]},
            itinerary=itinerary
        )
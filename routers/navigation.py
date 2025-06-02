from fastapi import APIRouter, Query, Depends, Form
from services.navigation_service import NavigationService
from schemas.schemas import RouteResponse


router = APIRouter()

@router.get("/route", response_model=RouteResponse)
async def get_route(
    user_id: str = Form(...),
    user_lat: float = Query(...),
    user_lon: float = Query(...),
    destination: str = Query(...),
    service: NavigationService = Depends()
):
    # 실제 서비스 로직
    # route_info = service.get_route(user_lon, user_lat, destination)
    # 시연 영상 촬영을 위한 고정 경로를 선택
    route_info = service.get_route_file(user_lon, user_lat, destination)
    service.store_user_itinerary(user_id, route_info['itinerary'])
    return route_info
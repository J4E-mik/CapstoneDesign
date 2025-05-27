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
    route_info = service.get_route(user_lon, user_lat, destination)
    service.store_user_itinerary(user_id, route_info['itinerary'])
    return route_info
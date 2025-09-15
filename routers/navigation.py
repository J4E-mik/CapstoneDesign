from fastapi import APIRouter, Query, Depends, Form
from services.navigation_service import NavigationService
from services.user_service import user_service
from services.session import user_session
from schemas.schemas import RouteResponse
from typing import Optional
import logging
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)
service = NavigationService()

@router.post("/route", response_model=RouteResponse)
async def get_route(
    user_id: str = Form(...),
    user_lat: Optional[float] = Form(None),
    user_lon: Optional[float] = Form(None),
    destination: str = Form(...)
):
    if user_lat is None or user_lon is None:
        user_lat, user_lon = {37.601519, 127.035367}
        # raise HTTPException(status_code=400, detail="GPS 정보 누락.")
    # 실제 서비스 로직
    # route_info = service.get_route(user_id, user_lon, user_lat, destination)
    # 시연 영상 촬영을 위한 고정 경로를 선택
    route_info = service.get_route_file(user_id, user_lon, user_lat, destination)

    logger.info(f"전체 경로 요청: \n\tuser_id:{user_id},\nitinerary:\n{route_info.itinerary}")
    logger.info(f"세션 정보: {user_service.user_information(user_id)}")
    return route_info

@router.get("/scores")
async def get_route_scores(user_id: str = Query(...), preference: str = Query("all")):
    session = user_session.get(user_id)
    if not session or "itineraries" not in session:
        return JSONResponse(content={"error":"No route data for this user."}, status_code=404)
    
    itineraries = session["itineraries"]
    score_list = service.get_score_breakdown(itineraries, preference)
    return JSONResponse(content=score_list)
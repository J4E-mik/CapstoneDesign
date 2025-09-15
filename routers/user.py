from fastapi import APIRouter, Depends, Form
from schemas.schemas import UserSessionResponse, UserIDResponse
from services.routing_service import RoutingService
from services.user_service import user_service
from services.feedback_service import feedback_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/connect", response_model=UserIDResponse)
async def connect_user():
    user_id = user_service.generate_user_id()
    logger.info(f"사용자 연결 요청: user_id:{user_id}")
    logger.info(f"세션 정보: {user_service.user_information(user_id)}")
    return {"user_id": user_id}

@router.post("/end_session", response_model=UserSessionResponse)
async def end_user_session(
    user_id: str = Form(...),
    routing_service: RoutingService = Depends()
):
    feedback_service.update_database()
    session_info = routing_service.end_session(user_id)
    logger.info(f"유저 세션 종료: user_id:{user_id}")
    logger.info(f"세션 정보: {user_service.user_information(user_id)}")
    return session_info

@router.post("/subway_navigation")
async def subway_navigation(
    user_id: str = Form(...),
    start_node_id: int = Form(...),
    goal_node_id: int =Form(...),
    routing_service: RoutingService = Depends()
):
    route_response = routing_service.initialize_subway_navigation(user_id, start_node_id, goal_node_id)
    routing_service.store_subwway_steps(user_id, route_response)
    logger.info(f"지하철 경로 요청:\n\tuser_id:{user_id},\n\tstart_node:{start_node_id},\n\tgoal_node:{goal_node_id},\nsteps:\n{route_response}")
    logger.info(f"세션 정보: {user_service.user_information(user_id)}")
    return route_response

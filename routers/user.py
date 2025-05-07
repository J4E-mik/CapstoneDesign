from fastapi import APIRouter, Depends, Form
from schemas.schemas import UserSessionResponse, UserIDResponse
from services.routing_service import RoutingService
from services.user_service import user_service


router = APIRouter()

@router.post("/connect", response_model=UserIDResponse)
async def connect_user():
    user_id = user_service.generate_user_id()
    return {"user_id": user_id}

@router.post("/start_session", response_model = UserSessionResponse)
async def start_user_session(
    user_id: str = Form(...),
    destination_node_id: int = Form(...),
    routing_service: RoutingService = Depends()
):
    session_info = routing_service.create_session(user_id, destination_node_id)
    return session_info

@router.post("/end_session", response_model=UserSessionResponse)
async def end_user_session(
    user_id: str = Form(...),
    routing_service: RoutingService = Depends()
):
    session_info = routing_service.end_session(user_id)
    return session_info

@router.post("/start_navigation", response_model = UserSessionResponse)
async def start_navigation(
    user_id: str = Form(...),
    current_node_id: int = Form(...),
    destination_node_type: int = Form(...),
    routing_service: RoutingService = Depends()
):
    session_info = routing_service.initialize_navigation_by_type(
        user_id, current_node_id, destination_node_type
    )
    return session_info

@router.post("/update_position", response_model=UserSessionResponse)
async def update_position(
    user_id: str = Form(...),
    current_node_id: int = Form(...),
    routing_service: RoutingService = Depends()
):
    next_node_info = routing_service.get_next_node(user_id, current_node_id)
    return next_node_info
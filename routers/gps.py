from fastapi import APIRouter, Form, Depends
from services.gps_service import GPSService
from services.user_service import user_service
from schemas.schemas import GPSUpdateResponse, GPSTrackResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/update", response_model=GPSUpdateResponse)
async def update_gps(
    user_id: str = Form(...), 
    lat: float = Form(...), 
    lon: float = Form(...),
    gps_service: GPSService = Depends()
):
    gps_response = gps_service.update_user_location(user_id, lon, lat)
    logger.info(f"GPS update 요청:\n\tuser_id:{user_id},\n\tlat:{lat},\n\tlon:{lon}")
    return gps_response

@router.post("/track", response_model=GPSTrackResponse)
async def track_route(
    user_id: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    gps_service: GPSService = Depends()
):
    gps_response = gps_service.track_user_route(user_id, lat, lon)
    return gps_response
from fastapi import APIRouter, Form, Depends
from services.gps_service import GPSService
from schemas.schemas import GPSUpdateResponse, GPSTrackResponse

router = APIRouter()


@router.post("/update", response_model=GPSUpdateResponse)
async def update_gps(
    user_id: str = Form(...), 
    lat: float = Form(...), 
    lon: float = Form(...),
    gps_service: GPSService = Depends()
):
    return gps_service.update_user_location(user_id, lon, lat)

@router.post("/track", response_model=GPSTrackResponse)
async def track_route(
    user_id: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    gps_service: GPSService = Depends()
):
    return gps_service.track_user_route(user_id, lat, lon)
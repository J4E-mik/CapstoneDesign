from fastapi import APIRouter, Form
from services.bus_service import get_bus_arrival_time

router = APIRouter()

@router.post("/bus/arrive")
async def bus_arrival_check(
    station_id: str=Form(...),
    route_id: str=Form(...)):
    arrival_info = get_bus_arrival_time(station_id, route_id)
    return {"arrival_info":arrival_info}
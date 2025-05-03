from fastapi import APIRouter, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from services.speech_service import transcribe_audio
from services.tmap import get_coordinates_by_keyword, get_transit_route
from services.guide_generator import generate_guide_messages, extract_walk_steps
from services.guide_voice import guide_messages_to_voice, voice_steps_to_files
from services.session import user_locations, user_session
from routers.gps import user_locations
import os

router = APIRouter()


@router.post("/route/stt")
async def route_from_audio(
    audio: UploadFile = File(...),
    user_id: str = Form(...)
):
    if user_id not in user_locations:
        return {"error":"NO GPS Info."}
    user_lon, user_lat = user_locations[user_id]

    keyword = await transcribe_audio(audio)

    dest_x, dest_y = get_coordinates_by_keyword(keyword)
    if not dest_x or not dest_y:
        return {"error": "Can Not Find a Destination"}
    
    route = get_transit_route((user_lon, user_lat), (dest_x, dest_y))
    if not route:
        return {"error": "Can Not Find a Route"}
    
    # 경로선택 하드코딩
    itinerary = route["metaData"]["plan"]["itineraries"][1]
    guide_messages = generate_guide_messages(itinerary)

    user_session[user_id] = {
    "walk_steps": extract_walk_steps(itinerary),
    "current_step_idx": 0,
    "tts_paths": guide_messages_to_voice(guide_messages),
    "itinerary": itinerary
}
    
    return {
        "destination": keyword,
        "start": {"lat":user_lat,"lon":user_lon},
        "end": {"lat":dest_y,"lon":dest_x},
        "itinerary": itinerary,
        "guides": guide_messages
    }

@router.post("/route/tts_guide")
async def route_from_audio(
    audio: UploadFile = File(...),
    user_id: str = Form(...)
):
    if user_id not in user_locations:
        return {"error":"NO GPS Info."}
    user_lon, user_lat = user_locations[user_id]

    keyword = await transcribe_audio(audio)

    dest_x, dest_y = get_coordinates_by_keyword(keyword)
    if not dest_x or not dest_y:
        return {"error": "Can Not Find a Destination"}
    
    route = get_transit_route((user_lon, user_lat), (dest_x, dest_y))
    if not route:
        return {"error": "Can Not Find a Route"}
    
    # 경로선택 하드코딩
    itinerary = route["metaData"]["plan"]["itineraries"][1]
    guide_messages = generate_guide_messages(itinerary)
    
    voice_files = guide_messages_to_voice(guide_messages)

    user_session[user_id] = {
    "walk_steps": extract_walk_steps(itinerary),
    "current_step_idx": 0,
    "tts_paths": guide_messages_to_voice(guide_messages),
    "itinerary": itinerary
}
    return {
        "destination": keyword,
        "voice_files": [f"/{os.path.relpath(path, start='static')}" for path in voice_files]
    }

# 디버깅 용
@router.get("/route")
async def get_route(
    user_lat: float=Query(...),
    user_lon: float=Query(...),
    destination: str = Query(...)
):
    dest_x, dest_y = get_coordinates_by_keyword(destination)
    if not dest_x or not dest_y:
        return {"error": "Can Not Find a Destination"}
    
    route = get_transit_route((user_lon, user_lat), (dest_x, dest_y))
    if not route:
        return {"error": "Can Not Find a Route"}
    
    # 경로 선택 부분 하드코딩
    itinerary = route["metadata"]["plan"]["itineraries"][1]
    return{
        "destination": destination,
        "itinerary": itinerary
    }
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GPSUpdateResponse(BaseModel):
    user: str
    message: str

class GPSTrackResponse(BaseModel):
    message: Optional[str] = None
    error: Optional[str] = None
    bus_number: Optional[str] = None
    stop_count: Optional[int] = None
    boarding_stop: Optional[str] = None
    alighting_stop: Optional[str] = None
    line_number: Optional[str] = None
    boarding_station: Optional[str] = None
    alighting_station: Optional[str] = None

class SpeechTranscriptionResponse(BaseModel):
    transcription: str

class Coordinate(BaseModel):
    lat: float
    lon: float

class RouteResponse(BaseModel):
    destination: str
    start: Coordinate
    end: Coordinate
    itinerary: Dict[str, Any]
    error: Optional[str] = None

class UserSessionResponse(BaseModel):
    user_id: str
    status: str
    next_node: Optional[int] = None
    total_cost: Optional[float] = None

class UserIDResponse(BaseModel):
    user_id: str
from fastapi import APIRouter, Form
from services.gps_tracker import is_within_step, is_within_radius
from services.session import user_locations, user_session

router = APIRouter()


@router.post("/update")
async def update_gps(
    user_id: str = Form(...), 
    lat: float=Form(...), 
    lon: float=Form(...)
):
    user_locations[user_id] = (lon,lat)
    return {
        "message": "GPS updated",
        "user": user_id
    }

@router.post("/track")
async def track_route(
    user_id: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    radius: float = Form(5.0)
):
    if user_id not in user_session:
        return {"error": "세션 정보가 없습니다."}

    session = user_session[user_id]
    itinerary = session["itinerary"]
    current_leg_idx = session.get("current_leg_idx", 0)
    legs = itinerary.get("legs", [])

    if current_leg_idx >= len(legs):
        return {"message": "모든 구간을 완료했습니다."}

    current_leg = legs[current_leg_idx]
    mode = current_leg.get("mode")

    # WALK 모드: step 기준 추적
    if mode == "WALK":
        steps = session["walk_steps"]
        step_idx = session.get("current_step_idx", 0)

        if step_idx >= len(steps):
            session["current_leg_idx"] += 1
            return {"message": f"WALK 구간 완료. 다음 구간으로 이동합니다."}

        step = steps[step_idx]
        if is_within_step(lat, lon, step["lat"], step["lon"], radius):
            session["current_step_idx"] += 1
            return {"message": f"WALK {step_idx+1}단계 도착: {step['text']}"}
        else:
            return {"message": f"WALK 진행 중: {step['text']}"}

    # BUS / SUBWAY 모드: leg 단위 도착지 판단
    elif mode in ["BUS", "SUBWAY"]:
        target_lat = current_leg["end"]["lat"]
        target_lon = current_leg["end"]["lon"]

        if is_within_radius((lat, lon), (target_lat, target_lon), radius):
            session["current_leg_idx"] += 1
            return {"message": f"{mode} 구간 종료. 다음 구간으로 이동합니다."}
        else:
            return {"message": f"{mode} 구간 진행 중..."}

    else:
        return {"message": f"지원하지 않는 모드: {mode}"}
    
# /track에 통합됨. 디버깅용
@router.post("/track/step")
async def track_user(
    user_id: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...)):
    if user_id not in user_session:
        return {"error": "진행 중인 경로가 없습니다."}
    
    session = user_session[user_id]
    steps = session.get("walk_steps", [])
    current_idx = session.get("current_step_idx", 0)

    if current_idx >= len(steps):
        return {"message": "WALK 구간이 완료되었습니다."}

    step = steps[current_idx]
    if is_within_step(lat, lon, step["lat"], step["lon"]):
        session["current_step_idx"] += 1
        return {
            "message": f"경유지 {current_idx + 1} 도착: {step['text']}",
            "next_step": steps[session["current_step_idx"]]["text"]
                if session["current_step_idx"] < len(steps) else "WALK 종료"
        }
    else:
        return {
            "message": f"현재 위치에서 {step['step_idx']+1}단계 경유지까지 이동 중입니다.",
            "target_text": step['text']
        }
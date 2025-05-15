import requests, time, json
from math import radians, sin, cos, sqrt, atan2

SERVER_URL = "http://"
USER_ID = None
ITINERARY = None
current_leg_idx = 0
current_step_idx = 0

def connect_server():
    global USER_ID
    response = requests.get(f"{SERVER_URL}/user/connect")
    USER_ID = response.json()["user_id"]
    print(f"Connect. User ID : {USER_ID}")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def is_arrived(current, target, radius=5.0):
    distance = haversine(current[0], current[1], target[0], target[1])
    return distance <= radius

def transcribe_audio(audio_file):
    with open(audio_file, "rb") as file:
        files = {"audio_file":file}
        response = requests.post(f"{SERVER_URL}/speech/stt", files=files)
    transcription = response.json()["transcription"]
    print(f"transcription result : {transcription}")
    return transcription

def get_current_gps():
    # 임시 코딩 GPS 모듈 에서 데이터 가져오는 로직 구현
    lat = 37.606
    lon = 127.041
    return lat, lon

def request_route(destination):
    lat, lon = get_current_gps()
    params = {
        "user_lat":lat,
        "user_lon":lon,
        "destination":destination
    }
    response = requests.get(f"{SERVER_URL}/nav/route", params=params)
    return response.json()["itinerary"]

def gps_update(lat, lon):
    data = {
        "user_id":USER_ID,
        "lat":lat,
        "lon":lon
    }
    requests.post(f"{SERVER_URL}/gps/update", data=data)

def gps_track(lat, lon):
    data = {
        "user_id":USER_ID,
        "lat":lat,
        "lon":lon
    }
    response = requests.post(f"{SERVER_URL}/gps/track", data=data)
    print(f"[DEBUG]: Tracking Response: {response.json()['message']}")

def main():
    global ITINERARY, current_leg_idx, current_step_idx
    connect_server()

    # 사용자 입력 대기
    audio_path = "audio.mp3" # 실제로 음성 녹음을 하면 변경
    destination = transcribe_audio(audio_path)
    ITINERARY = request_route(destination)

    if not ITINERARY:
        print("Error, No itinerary provided by server.")
        return
    
    legs = ITINERARY["legs"]
    print(f"[Navigation] 총 {len(legs)}개의 legs가 탐색됨")

    while current_leg_idx < len(legs):
        leg = legs[current_leg_idx]
        mode = leg["mode"]
        print(f"[Leg] Mode: {mode}, Leg idx: {current_leg_idx}")

        if mode == "WALK":
            steps = leg["steps"]
            while current_step_idx < len(steps):
                current_lat, current_lon = get_current_gps()
                step = steps[current_step_idx]
                end_coords = step["linestring"].split()[-1].split(",")
                end_lat, end_lon = map(float, end_coords)
                
                if is_arrived((current_lat, current_lon), (end_lat, end_lon)):
                    print(f"[Step] Step {current_step_idx} 도착: {step['text']}")
                    gps_update(current_lat, current_lon)
                    gps_track(current_lat, current_lon)
                    current_step_idx += 1
                else:
                    print(f"[Moving] Step {current_step_idx} 진행중: {step['text']}")
                
                time.sleep(1)

            current_step_idx = 0
            current_leg_idx += 1
        
        else:  # BUS, SUBWAY 등의 경우
            end_point = leg["end"]
            while True:
                current_lat, current_lon = get_current_gps()
                if is_arrived((current_lat, current_lon), (end_point["lat"], end_point["lon"])):
                    print(f"[Leg] {mode} 종료 지점 도착")
                    gps_update(current_lat, current_lon)
                    gps_track(current_lat, current_lon)
                    break
                else:
                    print(f"[Moving] {mode} 이용 중...")
                time.sleep(5)
            
            current_leg_idx += 1

    print("[Navigation] 목적지에 도착했습니다.")

if __name__ == '__main__':
    main()
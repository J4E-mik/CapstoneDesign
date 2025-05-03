import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote
import json


#출발지, 목적지 입력
origin = ""
destination = ""



# API 키 로드
load_dotenv()
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
REAL_TIME_SUB_KEY = os.getenv("REAL_TIME_SUB_KEY")
ENCODED_REAL_TIME_BUS_KEY = os.getenv("ENCODED_REAL_TIME_BUS_KEY")
DECODED_REAL_TIME_BUS_KEY = os.getenv("DECODED_REAL_TIME_BUS_KEY")



# API url들
# 노선 기반 실시간 버스 위치 조회
getBusPosByRtidList = f'http://ws.bus.go.kr/api/rest/buspos/getBusPosByRtidList'
# 차량 id 기반 위치 조회
getBusPosByVehid = f'http://ws.bus.go.kr/api/rest/buspos/getBusPosByVehId'
# 지하철 열차 위치 정보 조회
getSub = "http://swopenAPI.seoul.go.kr/api/subway/{REAL_TIME_SUB_KEY}/xml/realtimePosition/0/5/{SUB_LANE}"




# naver geocoding api
def get_coordinate(location):
    encoded_loaction = quote(location)
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={encoded_loaction}"
    
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
        "Accept": "application/json"
    }

    print(f"[DEBUG] Request URL:{url}")
    response = requests.get(url,headers=headers)
    print(f"[DEBUG] status code:{response.status_code}")
    print(f"[DEBUG] response:{response.text}")

    if response.status_code == 200:
        result = response.json()
        addresses = result.get("addresses")
        if addresses:
            x = addresses[0]["x"]
            y = addresses[0]["y"]
            return x,y
        else:
            print(f"Error:{location} Could not find.")
    else:
        print(f"Error:{response.status_code}")

origin_coord = get_coordinate(origin)
print(origin_coord)

#=========================================================================#
#=========================================================================#
#=========================================================================#
#=========================================================================#
#=========================================================================#
#=========================================================================#

from fastapi import FastAPI
from dotenv import load_dotenv
from urllib.parse import quote
import json, os, io, requests
import whisper

load_dotenv()
REAL_TIME_SUB_KEY = os.getenv("REAL_TIME_SUB_KEY")
ENCODED_REAL_TIME_BUS_KEY = os.getenv("ENCODED_REAL_TIME_BUS_KEY")
DECODED_REAL_TIME_BUS_KEY = os.getenv("DECODED_REAL_TIME_BUS_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
TMAP_APP_KEY=os.getenv("TMAP_APP_KEY")

TMAP_TRANSIT_URL = f'https://apis.openapi.sk.com/transit/routes'
TMAP_PEDESTRIAN_URL = f'https://apis.openapi.sk.com/tmap/jsv2?version=1&appKey={TMAP_APP_KEY}'

app = FastAPI()

# 주소기반 좌표 추출(현재 미사용)
def get_coordinate(location):
    encoded_loaction = quote(location)
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={encoded_loaction}"
    
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
        "Accept": "application/json"
    }
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        result = response.json()
        addresses = result.get("addresses")
        if addresses:
            x = addresses[0]["x"]
            y = addresses[0]["y"]
            return x,y
        else:
            print(f"Error:{location} Could not find.")
    else:
        print(f"Error:{response.status_code}")

# openai-whisper STT로 장소 추출
def get_keyword_by_STT(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, language='ko')
    return result["text"]

# STT로 추출한 장소에서 POI를 사용해 도착지 좌표 조회
def get_poi_keyword(keyword):
    TMAP_POI_URL=f'https://apis.openapi.sk.com/tmap/pois?version=1&appkey={TMAP_APP_KEY}&searchKeyword={keyword}'
    response = requests.get(TMAP_POI_URL)

    if response.status_code == 200:
        first_poi = response.json()["seachPoiInfo"]["pois"]["poi"][0]
        x = first_poi["frontLon"]
        y = first_poi["frontLat"]
        return x,y
    else:
        print(f"Error:{response.status_code}")

#start = "서울 성북구 종암로24길 35"
#end = "서울 성북구 동소문로 98"

# 음성 파일이 존재 하지 않아서 현재는 작동 불가 임시로 아래의 장소를 명시적으로 표시
#_keyword = get_keyword_by_STT(audio_file)
keyword = "처음처럼치과의원" # end와 주소 동일
# 현재는 하드 코딩으로 사용중. start_coord 위치 변경 요망
start_coord = [127.034272, 37.601454] # 아파트 외부 길에서 출발
end_coord = get_poi_keyword(keyword)

@app.get("/transit")
async def transit():
    payload = {
        "startX":start_coord[0],
        "startY":start_coord[1],
        "endX":end_coord[0],
        "endY":end_coord[1],
        "lang":0,
        "format":"json",
        #"count":10   
    }

    headers = {
        "accept":"application/json",
        "content-type":"application/json",
        "appKey":TMAP_APP_KEY
    }
    
    response = requests.post(TMAP_TRANSIT_URL, json=payload, headers=headers)
    return

'''
payload = {
        "startX":start_coord[0],
        "startY":start_coord[1],
        "endX":end_coord[0],
        "endY":end_coord[1],
        "lang":0,
        "format":"json",
        "count":10
    }

headers = {
    "accept":"application/json",
    "content-type":"application/json",
    "appKey":TMAP_APP_KEY
    }

response = requests.post(TMAP_TRANSIT_URL, json=payload, headers=headers)
print(response.text)
with open('data/transit_response.json', 'w', encoding='utf-8')as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)
'''
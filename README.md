Hierarchy
CapstoneDesign/ 
├── main.py 
├── config.py 
├── requirements.txt 
├── .env 
├── data/ 
│ ├── edge_table.csv 
│ ├── node_table.csv 
├── database/
│ ├── connection.py
│ ├── models.py
│ ├── routing.py
│ └── seed.py 
├── routers/ (엔드포인트 라우터 정의) 
│ ├── gps.py 
│ ├── navigation.py 
│ ├── speech.py 
│ └── user.py 
├── services/ (비즈니스 로직 및 외부 API 통신) 
│ ├── gps_service.py 
│ ├── speech_service.py 
│ ├── navigation_service.py 
│ └── routing_service.py 
├── schemas/ (Pydantic 데이터 모델 정의) 
│ └── schemas.py 
└── utils/ 
	└── gps_tracker.py

```
FASTAPI를 사용하는 서버
- 사용자는 웨어러블 장비(엣지 디바이스)를 착용(시각적 정보 불필요)
- 현재로는 사용자가 1명. 추후 여러명의 사용자를 고려해서 확장가능성
- GPS, IMU, 카메라 등의 센서 장비를 사용함
- 사용자의 음성 입력을 STT로 변환해서 키워드를 획득
- 획득한 키워드를 사용해 목적지의 WGS84 좌표를 획득
- 사용자의 현재 좌표(GPS모듈을 통해 획득)를 출발 좌표로 설정하여 TMAP transit API를 호출
- API응답에서 받은 Itineraries에서 경로 하나를 선택해서(해당 파일에서 Itineraries[1]인덱스에 있는 경로를 사용할 예정) 경로 안내를 시작
경로 안내 mode(WALK,BUS,SUBWAY)에 따라 안내 방식의 차이가 존재
Case: WALK
- 사용자가 서버로 지속적으로 GPS정보를 전송(아직 구현하지 못했지만 추후 IMU센서와 퓨전하여 보정을 할 예정 - 이 부분은 서버에서 처리하지 않고 엣지디바이스에서 처리될 가능성 큼) 사용자의 GPS정보를 기반으로 경유지에 도착을 구분(GPS상 오차범위를 임의설정하여 도착을 판별)하고 다음 이동을 위한 정보를 제공
Case: BUS
- 버스 정류소의 GPS정보(json에 포함)의 오차범위 내에 사용자가 도착했을 경우 선택한 경로에서 탑승해야하는 노선번호와 하차예정 정류소 그리고 이동하는 정류소의 수를 사용자에게 전송(json)
Case: SUBWAY
- 버스와 유사하게 GPS정보를 기반으로 지하철의 출발지, 도착지 정보를 획득 및 탑승해야하는 지하철 역 이름과 호선번호 하차예정 역과 이동하는 역의 수를 사용자에게 전송

경로 안내의 경우 엣지 디바이스에 미리 저장 된 음성안내를 재생하도록 json정보를 제공

주요 개발 예정 내용
SUBWAY mode인 경우 사용자로부터 지하철 역 내부에서의 이동정보를 POST받아서 데이터베이스에 구축되어 있는 라우팅 테이블을 기반으로 사용자가 가야하는 길 정보를 안내(알고리즘 구축 필요?)

준핵심내용 - 사용자의 정보를 관리하는 방법
구현요구사항 - 대부분의 기능들은 별개의 함수로 구현(모듈화) - 하나의 기능처럼 보이는 함수도 가능한 여러개의 모듈로 분할하여 라우터에서 각 모듈을 사용하도록 구현
```

<br><br><br><br>

|구현사항|구현여부|비고|
|-------|-------|---|
|사용자 음성 기반 키워드 추출|✅|Open AI Whisper사용 하여 STT|
|외부 API 호출 로직|✅|TMAP TRANSIT / TMAP POI 사용 중|
|사용자 정보 관리 및 경로 추적|✅|GPS 좌표 기반 위치 정보 저장|
|Mode별 서비스 로직|⚠️|mode:WALK 기능 위주 구현 완료|
|지하철 역 내부 Node 기반 라우팅 알고리즘|⚠️|IMU 데이터 부족으로 데이터베이스 쿼리만 구현|
|기능 모듈화|✅||

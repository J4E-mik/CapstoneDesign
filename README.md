Hierarchy \
CapstoneDesign/ \
├── main.py \
├── config.py \
├── requirements.txt \
├── .env \
├── data/ \
│ ├── edge_table.csv \
│ ├── node_table.csv \
├── database/ \
│ ├── connection.py \
│ ├── heuristic.py \
│ ├── models.py \
│ ├── routing.py \
│ └── seed.py \
├── routers/ (엔드포인트 라우터 정의) \
│ ├── gps.py \
│ ├── navigation.py \
│ ├── speech.py \
│ └── user.py \
├── services/ (비즈니스 로직 및 외부 API 통신) \
│ ├── feedback_service.py \
│ ├── gps_service.py \
│ ├── navigation_service.py \
│ ├── routing_service.py \
│ ├── session.py \
│ ├── speech_service.py \
│ └── user_service.py \
├── schemas/ (Pydantic 데이터 모델 정의) \
│ └── schemas.py \
└── utils/ \
	└── gps_tracker.py

```
FASTAPI를 사용하는 서버
- 사용자는 웨어러블 장비(엣지 디바이스)를 착용(시각적 정보 불필요)
- 현재로는 사용자가 1명. 추후 여러명의 사용자를 고려해서 확장가능성
- GPS, IMU, 카메라 등의 센서 장비를 사용함
- 사용자의 음성 입력을 STT로 변환해서 키워드를 획득
- 획득한 키워드를 사용해 목적지의 WGS84 좌표를 획득
- 사용자의 현재 좌표(GPS모듈을 통해 획득)를 출발 좌표로 설정하여 TMAP transit API를 호출
- API응답에서 받은 Itineraries에서 경로 하나를 선택해서 경로 안내를 시작
경로 안내 mode(WALK,BUS,SUBWAY)에 따라 안내 방식의 차이가 존재
Case: WALK
- 사용자가 서버로 지속적으로 GPS정보를 전송 사용자의 GPS정보를 기반으로 경유지에 도착을 구분(GPS상 오차범위를 임의설정하여 도착을 판별)하고 다음 이동을 위한 정보를 제공
Case: BUS
- 버스 정류소의 GPS정보(json에 포함)의 오차범위 내에 사용자가 도착했을 경우 선택한 경로에서 탑승해야하는 노선번호와 하차예정 정류소 그리고 이동하는 정류소의 수를 사용자에게 전송(json)
Case: SUBWAY
- 버스와 유사하게 GPS정보를 기반으로 지하철의 출발지, 도착지 정보를 획득 및 탑승해야하는 지하철 역 이름과 호선번호 하차예정 역과 이동하는 역의 수를 사용자에게 전송
- 사용자로부터 시작노드와 목적지 노드를 전달받고 이를 기반으로 a*알고리즘을 사용해 경로를 탐색 후 사용자에게 전체경로(json)를 전송
경로 생성과정에서 direct를 결정하기 위해 prev, current, next 3개의 노드의 좌표를 사용해 왼쪽, 오른쪽, 직진을 구분 {left:1, straight:2, right:3}
아마 벡터 외적을 사용해서 방향을 정할 예정
{
start: node_id(INT),
goal: node_id(INT),
	steps[...]{
		prev: node_id(INT),
		current: node_id(INT),
		next: node_id(INT),
		direct: node_id(INT)
	}
}

경로 안내의 경우 엣지 디바이스에 미리 저장 된 음성안내를 재생하도록 json정보를 제공

구현요구사항 - 대부분의 기능들은 별개의 함수로 구현(모듈화) - 하나의 기능처럼 보이는 함수도 가능한 여러개의 모듈로 분할하여 라우터에서 각 모듈을 사용하도록 구현
```

<br><br><br><br>

|구현사항|구현여부|비고|
|-------|-------|---|
|사용자 음성 기반 키워드 추출|✅|Open AI Whisper사용 하여 STT|
|외부 API 호출 로직|✅|TMAP TRANSIT / TMAP POI 사용 중|
|사용자 정보 관리 및 경로 추적|✅|GPS 좌표 기반 위치 정보 저장|
|Mode별 서비스 로직|✅|서비스 로직 구현 완료|
|지하철 역 내부 Node 기반 라우팅 |✅|A* 알고리즘 기반 라우팅|
|기능 모듈화|✅||
|서버 엔드 포인트 구현|⚠|설계 완료, 미구현|
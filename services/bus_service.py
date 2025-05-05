import requests, os, json, xmltodict
from dotenv import load_dotenv

load_dotenv()
BUS_API_KEY = os.getenv("DECODED_REAL_TIME_BUS_KEY")

def get_bus_arrival_time(station_id: str, route_id: str, ord: str) -> str:
    url = f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?"
    params = {
        "serviceKey": BUS_API_KEY,
        "stId": station_id,
        "busRouteId": route_id,
        "ord": ord
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            xml_data = response.text
            data_dict = xmltodict.parse(xml_data)
            json_data = json.dumps(data_dict, indent=4, ensure_ascii=False)
            with open('BusArrInfo.json', 'w', encoding='UTF-8') as f:
                f.write(json_data)
            return (xml_data)
        except Exception as e:    
            return f"도착 정보 처리 오류{str(e)}"
    else:
        return f"API 호출 실패:{response.status_code}"
    
route_id = '100100344'
station_id = '107000061'
ord = '29'
#print(get_bus_arrival_time(station_id, route_id, ord))
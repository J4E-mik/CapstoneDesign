import requests, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DECODED_REAL_TIME_BUS_KEY")

url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute'
params ={
    'serviceKey' : API_KEY, 
    'stId' : '124000414', 
    'busRouteId' : '100100578', 
    'ord' : '29'
}

response = requests.get(url, params=params)
print(response.content)
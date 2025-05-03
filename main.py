from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import speech, navigation, gps, bus    

app = FastAPI()

app.include_router(speech.router, prefix="/speech", tags=["Speech"])
app.include_router(navigation.router, prefix="nav", tags=["Navigation"])
app.include_router(gps.router, prefix="/gps", tags=["GPS"])
app.include_router(bus.router, prefix="/bus", tags=["Bus"])
app.mount("/voices", StaticFiles(directory="static/voices", name="voices"))
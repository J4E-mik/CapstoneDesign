from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import navigation, gps, speech, user
from config import settings
import logging

def create_app():
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION
    )

    app.include_router(navigation.router, prefix="/nav", tags=["Navigation"])
    app.include_router(gps.router, prefix="/gps", tags=["GPS"])
    app.include_router(speech.router, prefix="/speech", tags=["Speech"])
    app.include_router(user.router, prefix="/user", tags=["User"])
    
    return app

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = create_app()
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
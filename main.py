from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import navigation, gps, speech, user
from config import settings

def create_app():
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION
    )

    app.include_router(navigation.router, prefix="/nav", tags=["Navigation"])
    app.include_router(gps.router, prefix="/gps", tags=["GPS"])
    app.include_router(speech.router, prefix="/speech", tags=["Speech"])
    app.include_router(user.router, prefix="/user", tags=["User"])

    app.mount("/voices", StaticFiles(directory=settings.STATIC_VOICE_DIR), name="voices")

    return app

app = create_app()
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_TITLE: str = "Navigation Server"
    APP_VERSION: str = "1.0.0"

    
    DB_USER: str = os.getenv('DB_USER')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: str = os.getenv('DB_PORT')
    DB_NAME: str = os.getenv('DB_NAME')
    DATABASE_URL: str = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    )
    TMAP_APP_KEY = os.getenv("TMAP_APP_KEY")

    STATIC_VOICE_DIR = os.getenv("STATIC_VOICE_DIR", "static/voices")

settings = Settings()
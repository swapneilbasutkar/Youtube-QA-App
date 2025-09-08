"""
Env loading and configuration settings for the application.
"""

from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "Youtube Video Q&A API"
    VERSION: str = "1.0.0"
    CORS_ALLOW_ORIGINS = ["*"]

settings = Settings()
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///news_app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    NEWS_API_URL = os.getenv("NEWS_API_URL", "https://newsapi.org/v2")
    NEWS_API_TIMEOUT = int(os.getenv("NEWS_API_TIMEOUT", "30"))

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    GRADIO_SHARE = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    PAGINATION_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    NEWS_API_KEY = ""
    OLLAMA_HOST = "http://localhost:11434"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

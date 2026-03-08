import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _parse_cors_origins(raw_origins: str):
    """Parse CORS_ORIGINS env var into a Flask-CORS compatible value.

    Supported values:
    - "*" or "all": allow all origins
    - comma-separated origins: strict allowlist
    - "local": allow localhost/127.0.0.1 and private LAN ranges on any port
    """
    value = (raw_origins or "*").strip()
    if not value:
        return "*"

    if value.lower() in {"*", "all"}:
        return "*"

    local_origin_patterns = [
        r"^https?://localhost(:\d+)?$",
        r"^https?://127\.0\.0\.1(:\d+)?$",
        r"^https?://(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?$",
    ]

    parsed = []
    for item in value.split(","):
        token = item.strip().rstrip("/")
        if not token:
            continue
        lowered = token.lower()
        if lowered == "local":
            parsed.extend(local_origin_patterns)
            continue
        if lowered in {"*", "all"}:
            return "*"
        parsed.append(token)

    return parsed or "*"


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # MongoDB
    MONGODB_URI = os.getenv(
        "MONGODB_URI", 
        "mongodb://localhost:27017"  # local MongoDB fallback
    )
    MONGODB_DB = os.getenv("MONGODB_DB", "pieski_db")
    
    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", "local"))
    
    # Pagination
    ITEMS_PER_PAGE = 20

    # Email (SMTP)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database configuration
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if DATABASE_URL:
        # Use DATABASE_URL as-is without modifying it
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to individual variables
        DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
        DB_PORT = os.environ.get("DB_PORT", "5432")
        DB_USER = os.environ.get("DB_USER", "postgres")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "Malaba@2003")
        DB_NAME = os.environ.get("DB_NAME", "maize_disease_db")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
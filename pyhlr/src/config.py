import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server settings
    HLR_HOST: str = os.getenv('HLR_HOST', '0.0.0.0')
    HLR_PORT: int = int(os.getenv('HLR_PORT', '4222'))
    
    # Authentication service settings
    AUTH_SERVICE_URL: str = os.getenv('AUTH_SERVICE_URL', 'http://34.27.10.163:8080')
    AUTH_SERVICE_TIMEOUT: int = int(os.getenv('AUTH_SERVICE_TIMEOUT', '30'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    class Config:
        case_sensitive = True

settings = Settings() 
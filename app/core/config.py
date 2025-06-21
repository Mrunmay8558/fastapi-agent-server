from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    # App settings
    app_name: str = "FastAPI Agent Server"
    debug: bool = False
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    
    # Security settings
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days
    algorithm: str = "HS256"
    
    # CORS settings
    allowed_origins: List[str] = ["*"]  # In production, specify exact origins
    
    # Database settings
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "agent_server_db"
    db_connection_timeout: int = 10000  # milliseconds
    db_server_selection_timeout: int = 5000  # milliseconds
    db_max_pool_size: int = 10
    db_min_pool_size: int = 1
    db_max_idle_time: int = 30000  # milliseconds
    db_pull_time: int = 1000  # milliseconds - time to pull data
    db_retry_writes: bool = True
    db_retry_reads: bool = True
    
    # First superuser settings
    first_superuser_email: str = "admin@example.com"
    first_superuser_username: str = "admin"
    first_superuser_password: str = "changethis"
    
    # Email settings (for future use)
    smtp_tls: bool = True
    smtp_port: Optional[int] = None
    smtp_host: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    emails_from_email: Optional[str] = None
    emails_from_name: Optional[str] = None
    
    # Server settings
    server_name: str = "localhost"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
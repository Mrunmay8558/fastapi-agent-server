from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "FastAPI Agent Server"
    debug: bool = False
    version: str = "1.0.0"
    
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
    
    class Config:
        env_file = ".env"


settings = Settings()
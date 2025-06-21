from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    engine: Optional[AIOEngine] = None

db = Database()

async def get_database() -> AIOEngine:
    """Dependency to get database engine"""
    return db.engine

async def connect_to_mongo():
    """Create database connection with ODMantic"""
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.engine = AIOEngine(motor_client=db.client, database=settings.database_name)
    print(f"Connected to MongoDB at {settings.mongodb_url}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

# Database dependency for FastAPI
async def get_engine() -> AIOEngine:
    """FastAPI dependency for database engine"""
    return db.engine
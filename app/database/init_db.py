"""
Initial data creation for the database.
This script creates the first superuser and sets up necessary indexes.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.crud.crud_user import user as user_crud
from app.schemas.user import UserCreate


async def init_db() -> None:
    """
    Initialize database with first superuser and indexes
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    engine = AIOEngine(motor_client=client, database=settings.database_name)
    
    # Check if superuser exists
    superuser = await user_crud.get_by_email(engine, email=settings.first_superuser_email)
    
    if not superuser:
        print("Creating first superuser...")
        user_in = UserCreate(
            email=settings.first_superuser_email,
            username=settings.first_superuser_username,
            password=settings.first_superuser_password,
            first_name="Super",
            last_name="User",
            is_superuser=True,
        )
        superuser = await user_crud.create(engine, obj_in=user_in)
        print(f"Superuser created: {superuser.email}")
    else:
        print("Superuser already exists")
    
    # Create indexes for better performance
    await create_indexes(engine)
    
    await client.close()


async def create_indexes(engine: AIOEngine) -> None:
    """
    Create database indexes for better query performance
    """
    print("Creating database indexes...")
    
    # User collection indexes
    users_collection = engine.database["users"]
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("is_active")
    
    # Agent collection indexes
    agents_collection = engine.database["agents"]
    await agents_collection.create_index("name")
    await agents_collection.create_index("created_by")
    await agents_collection.create_index("is_active")
    await agents_collection.create_index([("name", "text"), ("description", "text")])  # Text search
    
    print("Database indexes created successfully")


if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(init_db())
    print("Database initialization completed")
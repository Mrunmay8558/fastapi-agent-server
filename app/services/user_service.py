from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database.mongodb import get_database
from app.models import User, PyObjectId
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self):
        self.collection_name = "users"

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        db = await get_database()
        
        # Check if user already exists
        existing_user = await db[self.collection_name].find_one({
            "$or": [
                {"email": user_data.email},
                {"username": user_data.username}
            ]
        })
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["agent_ids"] = []
        
        try:
            result = await db[self.collection_name].insert_one(user_dict)
            user_dict["_id"] = result.inserted_id
            return User(**user_dict)
        except DuplicateKeyError:
            raise ValueError("User with this email or username already exists")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = await get_database()
        user_data = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(**user_data)
        return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        db = await get_database()
        user_data = await db[self.collection_name].find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db = await get_database()
        user_data = await db[self.collection_name].find_one({"email": email})
        if user_data:
            return User(**user_data)
        return None

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db = await get_database()
        
        update_data = user_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            # Check for duplicate email/username if being updated
            if "email" in update_data or "username" in update_data:
                existing_user = await db[self.collection_name].find_one({
                    "$and": [
                        {"_id": {"$ne": ObjectId(user_id)}},
                        {"$or": [
                            {"email": update_data.get("email")},
                            {"username": update_data.get("username")}
                        ]}
                    ]
                })
                if existing_user:
                    raise ValueError("User with this email or username already exists")
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_user_by_id(user_id)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        db = await get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        db = await get_database()
        await db[self.collection_name].update_one(
            {"_id": user.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return user

    async def add_agent_to_user(self, user_id: str, agent_id: str) -> bool:
        """Add agent ID to user's agent list"""
        db = await get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"agent_ids": ObjectId(agent_id)}}
        )
        return result.modified_count > 0

    async def remove_agent_from_user(self, user_id: str, agent_id: str) -> bool:
        """Remove agent ID from user's agent list"""
        db = await get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"agent_ids": ObjectId(agent_id)}}
        )
        return result.modified_count > 0

    async def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Get list of users with pagination"""
        db = await get_database()
        users_data = await db[self.collection_name].find(
            {"is_active": True}
        ).skip(skip).limit(limit).to_list(length=limit)
        
        return [User(**user_data) for user_data in users_data]


user_service = UserService()
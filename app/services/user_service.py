from typing import Optional, List
from datetime import datetime
from odmantic import ObjectId
from odmantic.exceptions import DuplicateKeyError
from app.database.mongodb import get_database
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        engine = await get_database()

        # Check if user already exists
        existing_user = await engine.find_one(
            User,
            (User.email == user_data.email) | (User.username == user_data.username),
        )

        if existing_user:
            raise ValueError("User with this email or username already exists")

        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password

        user = User(**user_dict)

        try:
            return await engine.save(user)
        except DuplicateKeyError:
            raise ValueError("User with this email or username already exists")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        engine = await get_database()
        try:
            return await engine.find_one(User, User.id == ObjectId(user_id))
        except:
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        engine = await get_database()
        return await engine.find_one(User, User.username == username)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        engine = await get_database()
        return await engine.find_one(User, User.email == email)

    async def update_user(
        self, user_id: str, user_update: UserUpdate
    ) -> Optional[User]:
        """Update user information"""
        engine = await get_database()

        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            return None

        # Check for duplicate email/username if being updated
        if "email" in update_data or "username" in update_data:
            existing_user = await engine.find_one(
                User,
                (User.id != ObjectId(user_id))
                & (
                    (User.email == update_data.get("email"))
                    | (User.username == update_data.get("username"))
                ),
            )
            if existing_user:
                raise ValueError("User with this email or username already exists")

        # Update fields
        for field, value in update_data.items():
            setattr(user, field, value)
        user.updated_at = datetime.utcnow()

        return await engine.save(user)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()

        engine = await get_database()
        await engine.save(user)
        return True

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login time"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        engine = await get_database()
        await engine.save(user)
        return True

    async def add_agent_to_user(self, user_id: str, agent_id: str) -> bool:
        """Add agent ID to user's agent list"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        agent_obj_id = ObjectId(agent_id)
        if agent_obj_id not in user.agent_ids:
            user.agent_ids.append(agent_obj_id)
            user.updated_at = datetime.utcnow()

            engine = await get_database()
            await engine.save(user)
        return True

    async def remove_agent_from_user(self, user_id: str, agent_id: str) -> bool:
        """Remove agent ID from user's agent list"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        agent_obj_id = ObjectId(agent_id)
        if agent_obj_id in user.agent_ids:
            user.agent_ids.remove(agent_obj_id)
            user.updated_at = datetime.utcnow()

            engine = await get_database()
            await engine.save(user)
        return True

    async def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Get list of users with pagination"""
        engine = await get_database()
        return await engine.find(User, User.is_active == True, skip=skip, limit=limit)


user_service = UserService()

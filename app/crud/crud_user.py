from typing import Any, Dict, Optional, Union
from odmantic import AIOEngine
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, engine: AIOEngine, *, email: str) -> Optional[User]:
        """Get user by email"""
        return await engine.find_one(User, User.email == email)

    async def get_by_username(self, engine: AIOEngine, *, username: str) -> Optional[User]:
        """Get user by username"""
        return await engine.find_one(User, User.username == username)

    async def create(self, engine: AIOEngine, *, obj_in: UserCreate) -> User:
        """Create user with hashed password"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone=obj_in.phone,
            hashed_password=get_password_hash(obj_in.password),
        )
        return await engine.save(db_obj)

    async def update(
        self, engine: AIOEngine, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user with optional password hashing"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return await super().update(engine, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, engine: AIOEngine, *, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = await self.get_by_email(engine, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.is_superuser


user = CRUDUser(User)
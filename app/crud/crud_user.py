from typing import Any, Dict, Optional, Union, List
from odmantic import AIOEngine
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.agent import Agent
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, engine: AIOEngine, *, email: str) -> Optional[User]:
        """Get user by email"""
        return await engine.find_one(User, User.email == email)

    async def get_by_username(
        self, engine: AIOEngine, *, username: str
    ) -> Optional[User]:
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
        self,
        engine: AIOEngine,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
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

    async def authenticate(
        self, engine: AIOEngine, *, email: str, password: str
    ) -> Optional[User]:
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

    async def get_with_agents(
        self, engine: AIOEngine, *, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user with populated agent models"""
        user = await self.get(engine, id=user_id)
        if not user:
            return None

        # Fetch all agents for this user
        agents = await engine.find(Agent, Agent.id.in_(user.agent_ids))

        # Convert to dict and add populated agents
        user_dict = user.dict()
        user_dict["agents"] = [agent.dict() for agent in agents]

        return user_dict

    async def get_multi_with_agents(
        self, engine: AIOEngine, *, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get multiple users with populated agent models"""
        users = await self.get_multi(engine, skip=skip, limit=limit)

        result = []
        for user in users:
            # Fetch agents for each user
            agents = await engine.find(Agent, Agent.id.in_(user.agent_ids))

            user_dict = user.dict()
            user_dict["agents"] = [agent.dict() for agent in agents]
            result.append(user_dict)

        return result

    async def get_user_agents(self, engine: AIOEngine, *, user_id: str) -> List[Agent]:
        """Get all agents belonging to a specific user"""
        user = await self.get(engine, id=user_id)
        if not user:
            return []

        return await engine.find(Agent, Agent.id.in_(user.agent_ids))


user = CRUDUser(User)

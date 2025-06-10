from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.database.mongodb import get_database
from app.models import Agent, PyObjectId
from app.schemas import AgentCreate, AgentUpdate
from app.services.user_service import user_service


class AgentService:
    def __init__(self):
        self.collection_name = "agents"

    async def create_agent(self, agent_data: AgentCreate, user_id: str) -> Agent:
        """Create a new agent for a user"""
        db = await get_database()
        
        # Verify user exists
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        agent_dict = agent_data.dict()
        agent_dict["created_by"] = ObjectId(user_id)
        agent_dict["created_at"] = datetime.utcnow()
        agent_dict["updated_at"] = datetime.utcnow()
        
        result = await db[self.collection_name].insert_one(agent_dict)
        agent_dict["_id"] = result.inserted_id
        
        # Add agent to user's agent list
        await user_service.add_agent_to_user(user_id, str(result.inserted_id))
        
        return Agent(**agent_dict)

    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        db = await get_database()
        agent_data = await db[self.collection_name].find_one({"_id": ObjectId(agent_id)})
        if agent_data:
            return Agent(**agent_data)
        return None

    async def get_agents_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Agent]:
        """Get all agents created by a specific user"""
        db = await get_database()
        agents_data = await db[self.collection_name].find(
            {"created_by": ObjectId(user_id), "is_active": True}
        ).skip(skip).limit(limit).to_list(length=limit)
        
        return [Agent(**agent_data) for agent_data in agents_data]

    async def update_agent(self, agent_id: str, agent_update: AgentUpdate, user_id: str) -> Optional[Agent]:
        """Update agent information (only by creator)"""
        db = await get_database()
        
        # Check if agent exists and user is the creator
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        if str(agent.created_by) != user_id:
            raise ValueError("Permission denied: You can only update agents you created")
        
        update_data = agent_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(agent_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_agent_by_id(agent_id)
        return None

    async def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """Delete agent (soft delete by setting is_active to False)"""
        db = await get_database()
        
        # Check if agent exists and user is the creator
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        if str(agent.created_by) != user_id:
            raise ValueError("Permission denied: You can only delete agents you created")
        
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count:
            # Remove agent from user's agent list
            await user_service.remove_agent_from_user(user_id, agent_id)
            return True
        return False

    async def get_agents(self, skip: int = 0, limit: int = 10) -> List[Agent]:
        """Get list of all active agents (admin function)"""
        db = await get_database()
        agents_data = await db[self.collection_name].find(
            {"is_active": True}
        ).skip(skip).limit(limit).to_list(length=limit)
        
        return [Agent(**agent_data) for agent_data in agents_data]

    async def search_agents(self, query: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[Agent]:
        """Search agents by name or description"""
        db = await get_database()
        
        search_filter = {
            "is_active": True,
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if user_id:
            search_filter["created_by"] = ObjectId(user_id)
        
        agents_data = await db[self.collection_name].find(
            search_filter
        ).skip(skip).limit(limit).to_list(length=limit)
        
        return [Agent(**agent_data) for agent_data in agents_data]

    async def get_agent_stats(self, user_id: str) -> dict:
        """Get agent statistics for a user"""
        db = await get_database()
        
        pipeline = [
            {"$match": {"created_by": ObjectId(user_id)}},
            {"$group": {
                "_id": None,
                "total_agents": {"$sum": 1},
                "active_agents": {"$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}},
                "inactive_agents": {"$sum": {"$cond": [{"$eq": ["$is_active", False]}, 1, 0]}}
            }}
        ]
        
        result = await db[self.collection_name].aggregate(pipeline).to_list(length=1)
        
        if result:
            stats = result[0]
            del stats["_id"]
            return stats
        
        return {"total_agents": 0, "active_agents": 0, "inactive_agents": 0}


agent_service = AgentService()
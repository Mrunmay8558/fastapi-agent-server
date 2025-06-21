from typing import List, Optional
from odmantic import AIOEngine, ObjectId
from app.crud.base import CRUDBase
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def get_by_user(
        self, engine: AIOEngine, *, owner_id: str, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """Get agents created by a specific user"""
        return await engine.find(
            Agent,
            (Agent.created_by == ObjectId(owner_id)) & (Agent.is_active == True),
            skip=skip,
            limit=limit
        )

    async def get_by_name(self, engine: AIOEngine, *, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return await engine.find_one(Agent, Agent.name == name)

    async def search(
        self, 
        engine: AIOEngine, 
        *, 
        query: str, 
        owner_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Agent]:
        """Search agents by name or description"""
        # Build base filter
        search_filter = Agent.is_active == True
        
        if owner_id:
            search_filter = search_filter & (Agent.created_by == ObjectId(owner_id))
        
        # Get all matching agents first
        agents = await engine.find(Agent, search_filter, skip=skip, limit=limit)
        
        # Filter by query in Python (for now, until text search indexes are set up)
        filtered_agents = []
        for agent in agents:
            if (query.lower() in agent.name.lower() or 
                (agent.description and query.lower() in agent.description.lower())):
                filtered_agents.append(agent)
        
        return filtered_agents

    async def get_active(
        self, engine: AIOEngine, *, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """Get all active agents"""
        return await engine.find(
            Agent, Agent.is_active == True, skip=skip, limit=limit
        )

    async def get_stats_by_user(self, engine: AIOEngine, *, owner_id: str) -> dict:
        """Get agent statistics for a user"""
        all_agents = await engine.find(Agent, Agent.created_by == ObjectId(owner_id))
        
        total_agents = len(all_agents)
        active_agents = len([a for a in all_agents if a.is_active])
        inactive_agents = total_agents - active_agents
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "inactive_agents": inactive_agents
        }


agent = CRUDAgent(Agent)
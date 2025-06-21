from typing import Optional, List
from datetime import datetime
from odmantic import ObjectId
from app.database.mongodb import get_database
from app.models import Agent
from app.schemas import AgentCreate, AgentUpdate
from app.services.user_service import user_service


class AgentService:
    async def create_agent(self, agent_data: AgentCreate, user_id: str) -> Agent:
        """Create a new agent for a user"""
        engine = await get_database()

        # Verify user exists
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        agent_dict = agent_data.dict()
        agent_dict["created_by"] = ObjectId(user_id)

        agent = Agent(**agent_dict)
        saved_agent = await engine.save(agent)

        # Add agent to user's agent list
        await user_service.add_agent_to_user(user_id, str(saved_agent.id))

        return saved_agent

    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        engine = await get_database()
        try:
            return await engine.find_one(Agent, Agent.id == ObjectId(agent_id))
        except:
            return None

    async def get_agents_by_user(
        self, user_id: str, skip: int = 0, limit: int = 10
    ) -> List[Agent]:
        """Get all agents created by a specific user"""
        engine = await get_database()
        return await engine.find(
            Agent,
            (Agent.created_by == ObjectId(user_id)) & (Agent.is_active == True),
            skip=skip,
            limit=limit,
        )

    async def update_agent(
        self, agent_id: str, agent_update: AgentUpdate, user_id: str
    ) -> Optional[Agent]:
        """Update agent information (only by creator)"""
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Agent not found")

        if str(agent.created_by) != user_id:
            raise ValueError(
                "Permission denied: You can only update agents you created"
            )

        update_data = agent_update.dict(exclude_unset=True)
        if not update_data:
            return None

        # Update fields
        for field, value in update_data.items():
            setattr(agent, field, value)
        agent.updated_at = datetime.utcnow()

        engine = await get_database()
        return await engine.save(agent)

    async def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """Delete agent (soft delete by setting is_active to False)"""
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Agent not found")

        if str(agent.created_by) != user_id:
            raise ValueError(
                "Permission denied: You can only delete agents you created"
            )

        agent.is_active = False
        agent.updated_at = datetime.utcnow()

        engine = await get_database()
        await engine.save(agent)

        # Remove agent from user's agent list
        await user_service.remove_agent_from_user(user_id, agent_id)
        return True

    async def get_agents(self, skip: int = 0, limit: int = 10) -> List[Agent]:
        """Get list of all active agents (admin function)"""
        engine = await get_database()
        return await engine.find(Agent, Agent.is_active == True, skip=skip, limit=limit)

    async def search_agents(
        self, query: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 10
    ) -> List[Agent]:
        """Search agents by name or description"""
        engine = await get_database()

        # Build search filter
        search_filter = Agent.is_active == True

        if user_id:
            search_filter = search_filter & (Agent.created_by == ObjectId(user_id))

        # Note: ODMantic doesn't support regex queries directly in the find method
        # For text search, you might want to use the raw motor client or implement full-text search
        # For now, we'll do a simple case-insensitive contains search
        agents = await engine.find(Agent, search_filter, skip=skip, limit=limit)

        # Filter results in Python for now (not optimal for large datasets)
        filtered_agents = []
        for agent in agents:
            if query.lower() in agent.name.lower() or (
                agent.description and query.lower() in agent.description.lower()
            ):
                filtered_agents.append(agent)

        return filtered_agents

    async def get_agent_stats(self, user_id: str) -> dict:
        """Get agent statistics for a user"""
        engine = await get_database()

        # Get all agents for the user
        all_agents = await engine.find(Agent, Agent.created_by == ObjectId(user_id))

        total_agents = len(all_agents)
        active_agents = len([a for a in all_agents if a.is_active])
        inactive_agents = total_agents - active_agents

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "inactive_agents": inactive_agents,
        }


agent_service = AgentService()

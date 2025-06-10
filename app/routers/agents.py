from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.schemas import (
    AgentCreate, AgentUpdate, AgentResponse,
    MessageResponse, ErrorResponse
)
from app.services.agent_service import agent_service
from app.utils.auth import get_current_active_user
from app.models import User

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new agent"""
    try:
        agent = await agent_service.create_agent(agent_data, str(current_user.id))
        return AgentResponse(**agent.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[AgentResponse])
async def get_my_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all agents created by the current user"""
    agents = await agent_service.get_agents_by_user(
        str(current_user.id), skip=skip, limit=limit
    )
    return [AgentResponse(**agent.dict()) for agent in agents]


@router.get("/search", response_model=List[AgentResponse])
async def search_agents(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Search agents by name or description (only user's own agents)"""
    agents = await agent_service.search_agents(
        q, user_id=str(current_user.id), skip=skip, limit=limit
    )
    return [AgentResponse(**agent.dict()) for agent in agents]


@router.get("/stats")
async def get_agent_stats(current_user: User = Depends(get_current_active_user)):
    """Get agent statistics for the current user"""
    stats = await agent_service.get_agent_stats(str(current_user.id))
    return stats


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific agent by ID"""
    agent = await agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user owns this agent
    if str(agent.created_by) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: You can only view agents you created"
        )
    
    return AgentResponse(**agent.dict())


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update an agent"""
    try:
        updated_agent = await agent_service.update_agent(
            agent_id, agent_update, str(current_user.id)
        )
        if not updated_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made or agent not found"
            )
        return AgentResponse(**updated_agent.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{agent_id}", response_model=MessageResponse)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete an agent (soft delete)"""
    try:
        success = await agent_service.delete_agent(agent_id, str(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete agent"
            )
        return MessageResponse(message="Agent deleted successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/all/admin", response_model=List[AgentResponse])
async def get_all_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all agents (admin function - you may want to add admin role check)"""
    agents = await agent_service.get_agents(skip=skip, limit=limit)
    return [AgentResponse(**agent.dict()) for agent in agents]
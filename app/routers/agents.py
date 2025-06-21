from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from odmantic import AIOEngine

from app import crud, schemas
from app.database.mongodb import get_engine
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=schemas.Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: schemas.AgentCreate,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Create a new agent"""
    # Check if agent with same name already exists for this user
    existing_agent = await crud.agent.get_by_name(engine, name=agent_data.name)
    if existing_agent and existing_agent.created_by == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Agent with this name already exists for your account",
        )
    
    # Create agent with current user as owner
    agent_dict = agent_data.dict()
    agent_dict["created_by"] = current_user.id
    agent = await crud.agent.create(engine, obj_in=schemas.AgentCreate(**agent_dict))
    
    return agent


@router.get("/", response_model=List[schemas.Agent])
async def get_user_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Get current user's agents"""
    agents = await crud.agent.get_by_user(
        engine, owner_id=str(current_user.id), skip=skip, limit=limit
    )
    return agents


@router.get("/search", response_model=List[schemas.Agent])
async def search_agents(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Search user's agents by name or description"""
    agents = await crud.agent.search(
        engine, query=q, owner_id=str(current_user.id), skip=skip, limit=limit
    )
    return agents


@router.get("/stats", response_model=dict)
async def get_agent_stats(
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Get agent statistics for current user"""
    stats = await crud.agent.get_stats_by_user(engine, owner_id=str(current_user.id))
    return stats


@router.get("/{agent_id}", response_model=schemas.Agent)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Get specific agent by ID"""
    agent = await crud.agent.get(engine, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if user owns this agent
    if agent.created_by != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this agent"
        )
    
    return agent


@router.put("/{agent_id}", response_model=schemas.Agent)
async def update_agent(
    agent_id: str,
    agent_update: schemas.AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Update agent"""
    agent = await crud.agent.get(engine, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if user owns this agent
    if agent.created_by != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this agent"
        )
    
    agent = await crud.agent.update(engine, db_obj=agent, obj_in=agent_update)
    return agent


@router.delete("/{agent_id}", response_model=schemas.Msg)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Delete agent (soft delete)"""
    agent = await crud.agent.get(engine, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if user owns this agent
    if agent.created_by != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this agent"
        )
    
    # Soft delete by setting is_active to False
    await crud.agent.update(
        engine, db_obj=agent, obj_in={"is_active": False}
    )
    
    return schemas.Msg(msg="Agent deleted successfully")
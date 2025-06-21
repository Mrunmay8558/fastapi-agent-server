from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from odmantic import AIOEngine

from app import crud, schemas
from app.database.mongodb import get_engine
from app.core.security import (
    get_current_active_user,
    get_current_active_superuser,
    create_access_token,
)
from app.core.config import settings
from app.models.user import User

router = APIRouter()


@router.post(
    "/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: schemas.UserCreate, engine: AIOEngine = Depends(get_engine)
):
    """Register a new user"""
    user = await crud.user.get_by_email(engine, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.user.create(engine, obj_in=user_data)
    return user


@router.post("/login", response_model=schemas.LoginResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    engine: AIOEngine = Depends(get_engine),
):
    """Login user and return JWT token with user data"""
    user = await crud.user.authenticate(
        engine, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return schemas.LoginResponse(
        access_token=access_token, token_type="bearer", user=user.dict()
    )


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Update current user information"""
    user = await crud.user.update(engine, db_obj=current_user, obj_in=user_update)
    return user


@router.get("/", response_model=List[schemas.User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_superuser),
    engine: AIOEngine = Depends(get_engine),
):
    """Get list of users (superuser only)"""
    users = await crud.user.get_multi(engine, skip=skip, limit=limit)
    return users


@router.get("/with-agents", response_model=List[schemas.UserWithAgents])
async def get_users_with_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_superuser),
    engine: AIOEngine = Depends(get_engine),
):
    """Get list of users with populated agent models (superuser only)"""
    users_with_agents = await crud.user.get_multi_with_agents(
        engine, skip=skip, limit=limit
    )
    return users_with_agents


@router.get("/me/with-agents", response_model=schemas.UserWithAgents)
async def get_current_user_with_agents(
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Get current user with populated agent models"""
    user_with_agents = await crud.user.get_with_agents(
        engine, user_id=str(current_user.id)
    )
    if not user_with_agents:
        raise HTTPException(status_code=404, detail="User not found")
    return user_with_agents


@router.get("/{user_id}/with-agents", response_model=schemas.UserWithAgents)
async def get_user_with_agents(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Get a specific user with populated agent models"""
    # Check permissions
    if str(current_user.id) != user_id and not await crud.user.is_superuser(
        current_user
    ):
        raise HTTPException(status_code=400, detail="Not enough privileges")

    user_with_agents = await crud.user.get_with_agents(engine, user_id=user_id)
    if not user_with_agents:
        raise HTTPException(status_code=404, detail="User not found")
    return user_with_agents


@router.get("/{user_id}/agents", response_model=List[schemas.Agent])
async def get_user_agents(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    engine: AIOEngine = Depends(get_engine),
):
    """Get all agents belonging to a specific user"""
    # Check permissions
    if str(current_user.id) != user_id and not await crud.user.is_superuser(
        current_user
    ):
        raise HTTPException(status_code=400, detail="Not enough privileges")

    agents = await crud.user.get_user_agents(engine, user_id=user_id)
    return agents

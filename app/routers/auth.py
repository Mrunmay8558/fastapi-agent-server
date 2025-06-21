from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from odmantic import AIOEngine

from app import crud, schemas
from app.database.mongodb import get_engine
from app.core.security import create_access_token, get_current_active_user
from app.core.config import settings

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    engine: AIOEngine = Depends(get_engine),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        engine, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not await crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return {
        "access_token": create_access_token(
            subject=user.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=schemas.User)
async def test_token(current_user: Any = Depends(get_current_active_user)) -> Any:
    """
    Test access token
    """
    return current_user

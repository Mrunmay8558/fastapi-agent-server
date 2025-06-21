from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from app.services.user_service import user_service
from app.models import User

# OAuth2PasswordBearer with token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # Handle both standard JWT and custom signJWT token formats
    user_id = payload.get("user_id") or payload.get("sub")
    email = payload.get("email")
    
    if not user_id and not email:
        raise credentials_exception
    
    # Try to get user by user_id first, then by email if available
    user = None
    if user_id:
        user = await user_service.get_user_by_id(user_id)
    elif email:
        user = await user_service.get_user_by_email(email)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
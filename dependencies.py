# backend/dependencies.py
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.db import get_db
from backend.core.security import decode_access_token
import logging
from backend.models import User

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """
    Extracts the bearer token from Authorization header and returns the User model.
    Header must be: Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    # payload should contain sub as user id
    user_id = payload.get("sub") or payload.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    # Use SQLAlchemy 2.x syntax
    try:
        user = db.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
    except ValueError:
        # Handle case where user_id is not an int (e.g. if using uuid or string)
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

def get_current_user_optional(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """
    Returns User if token is valid, else None. Does not raise HTTPException.
    """
    if not authorization:
        return None
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub") or payload.get("id")
    if not user_id:
        return None
    
    try:
        user = db.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
        return user
    except:
        return None

def get_current_active_user(current_user: User = Depends(get_current_user)):
    # extend with checks (is_active) if you add that field
    return current_user

def require_teacher(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required")
    return current_user

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.api.auth import get_current_user, get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserPublic, UserUpdate, UserPasswordUpdate
from app.services import user_service

router = APIRouter()

@router.get("/search", response_model=List[UserPublic])
def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for users by username or full name.
    """
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) | 
        (User.full_name.ilike(f"%{q}%"))
    ).limit(limit).all()
    
    # Convert to UserPublic with follower counts
    result = []
    for user in users:
        result.append(UserPublic(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            profile_picture_url=user.profile_picture_url,
            created_at=user.created_at,
            followers_count=len(user.followers),
            following_count=len(user.following)
        ))
    return result

@router.get("/me", response_model=UserSchema)
def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Get current user details.
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update own profile.
    """
    if user_in.username and user_in.username != current_user.username:
        existing_user = user_service.get_by_username(db, user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
            
    updated_user = user_service.update_user(db, current_user, user_in)
    return updated_user

@router.get("/{username}", response_model=UserPublic)
def read_user(username: str, db: Session = Depends(get_db)):
    """
    Get specific user profile by username (Public info only).
    """
    user_public = user_service.get_public_profile(db, username)
    if not user_public:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_public

@router.put("/me/password")
def update_password_me(
    password_in: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update password with complexity checks.
    """
    from app.core.security import verify_password, get_password_hash
    import re

    # 1. Verify current password
    if not verify_password(password_in.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # 2. Validate new password complexity
    password = password_in.new_password
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")
    if len(password) > 72:
        raise HTTPException(status_code=400, detail="Password cannot be longer than 72 characters")

    # 3. Update password
    current_user.password_hash = get_password_hash(password)
    db.commit()
    
    return {"message": "Password updated successfully"}


from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.schemas.user import User as UserSchema, UserPublic, UserUpdate, UserPasswordUpdate
from app.services import user_service
from app.models.user import User

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
    return user_service.search_users(db, q, limit)

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
    result = user_service.update_password(
        db, current_user, password_in.current_password, password_in.new_password
    )
    
    if result != "ok":
         raise HTTPException(status_code=400, detail=result)
    
    return {"message": "Password updated successfully"}


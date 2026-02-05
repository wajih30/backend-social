import re
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate, UserPublic
from app.core.security import verify_password, get_password_hash
from typing import Optional

def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    if user_in.username:
        # Caller should verify uniqueness if needed, or handle IntegrityError
        db_user.username = user_in.username
    if user_in.full_name is not None:
        db_user.full_name = user_in.full_name
    if user_in.bio is not None:
        db_user.bio = user_in.bio
    if user_in.profile_picture_url is not None:
        db_user.profile_picture_url = user_in.profile_picture_url
        
    db.commit()
    db.refresh(db_user)
    return db_user

def get(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_public_profile(db: Session, username: str) -> Optional[UserPublic]:
    user = get_by_username(db, username)
    if not user:
        return None
        
    followers_count = len(user.followers)
    following_count = len(user.following)
    
    return UserPublic(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        bio=user.bio,
        profile_picture_url=user.profile_picture_url,
        created_at=user.created_at,
        followers_count=followers_count,
        following_count=following_count
    )

def search_users(db: Session, query: str, limit: int = 20) -> list[UserPublic]:
    users = db.query(User).filter(
        (User.username.ilike(f"%{query}%")) | 
        (User.full_name.ilike(f"%{query}%"))
    ).limit(limit).all()
    
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

def validate_password_complexity(password: str) -> Optional[str]:
    """
    Validate password complexity. Returns None if valid, or a descriptive error message.
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character"
    if len(password) > 72:
        return "Password cannot be longer than 72 characters"
    return None

def update_password(db: Session, user: User, current_password: str, new_password: str) -> str:
    # 1. Verify current password
    if not verify_password(current_password, user.password_hash):
        return "Incorrect current password"

    # 2. Validate new password complexity
    error = validate_password_complexity(new_password)
    if error:
        return error

    # 3. Update password
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return "ok"

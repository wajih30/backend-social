from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate, UserPublic
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

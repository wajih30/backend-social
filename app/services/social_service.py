from sqlalchemy.orm import Session
from app.models.follow import Follow
from app.models.user import User
from app.models.notification import Notification, NotificationType
from fastapi import HTTPException

def follow_user(db: Session, follower_id: int, following_id: int):
    if follower_id == following_id:
        
        raise HTTPException(status_code=400, detail="You cannot follow yourself.")
        
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id
    ).first()
    
    if existing_follow:
        
        raise HTTPException(status_code=400, detail="You are already following this user.")
        
    new_follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(new_follow)
    
    # Create Notification
    notification = Notification(
        receiver_id=following_id,
        sender_id=follower_id,
        type=NotificationType.follow
    )
    db.add(notification)
    
    db.commit()
    db.refresh(new_follow)
    return new_follow

def unfollow_user(db: Session, follower_id: int, following_id: int):
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id
    ).first()
    
    if existing_follow:
        db.delete(existing_follow)
        db.commit()
        return True
    return False

def is_following(db: Session, follower_id: int, following_id: int) -> bool:
    return db.query(Follow).filter(
        Follow.follower_id == follower_id, 
        Follow.following_id == following_id
    ).first() is not None

def get_followers(db: Session, user_id: int):
    """
    Get list of users responding to who follows the given user_id.
    """
    return db.query(User).join(Follow, Follow.follower_id == User.id).filter(
        Follow.following_id == user_id
    ).all()

def get_following(db: Session, user_id: int):
    """
    Get list of users that the given user_id is following.
    """
    return db.query(User).join(Follow, Follow.following_id == User.id).filter(
        Follow.follower_id == user_id
    ).all()

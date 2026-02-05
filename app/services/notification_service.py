from sqlalchemy.orm import Session
from typing import List
from app.models.notification import Notification
from app.models.user import User

def get_my_notifications(db: Session, user_id: int, limit: int = 20, skip: int = 0) -> List[Notification]:
    return db.query(Notification).filter(
        Notification.receiver_id == user_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_all_as_read(db: Session, user_id: int):
    db.query(Notification).filter(
        Notification.receiver_id == user_id,
        Notification.is_read == False
    ).update({Notification.is_read: True}, synchronize_session=False)
    db.commit()

def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(
        Notification.receiver_id == user_id,
        Notification.is_read == False
    ).count()


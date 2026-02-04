from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.api.auth import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import Notification as NotificationSchema
from app.services import notification_service

router = APIRouter()

@router.get("/", response_model=List[NotificationSchema])
def get_notifications(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's notifications.
    """
    return notification_service.get_my_notifications(db, current_user.id, limit, skip)

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a specific notification as read.
    """
    success = notification_service.mark_as_read(db, current_user.id, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all unread notifications as read.
    """
    notification_service.mark_all_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the count of unread notifications.
    """
    count = notification_service.get_unread_count(db, current_user.id)
    return {"count": count}


from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserPublic
from app.models.notification import NotificationType

class NotificationBase(BaseModel):
    pass

class Notification(NotificationBase):
    id: int
    receiver_id: int
    sender_id: int
    sender: Optional[UserPublic] = None
    type: NotificationType

    post_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

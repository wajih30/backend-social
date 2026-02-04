from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserPublic

# --- Post Schemas ---
class PostBase(BaseModel):
    content_text: str
    caption: Optional[str] = None
    media_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content_text: Optional[str] = None
    caption: Optional[str] = None
    media_url: Optional[str] = None

class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: UserPublic
    likes_count: int = 0
    comments_count: int = 0
    is_liked_by_me: bool = False # Helper for UI

    class Config:
        from_attributes = True

# --- Comment Schemas ---

class CommentBase(BaseModel):
    comment_text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    user: UserPublic # Owner of the comment

    class Config:
        from_attributes = True

# --- Like Schemas ---
# No special schema needed for create usually (just post_id in URL), but we can have one
class LikeCreate(BaseModel):
    post_id: int

class PostDetail(Post):
    comments: List[Comment] = []


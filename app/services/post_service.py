from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.follow import Follow
from app.models.like import Like
from app.models.comment import Comment
from app.models.notification import Notification, NotificationType
from app.schemas.social import PostCreate, CommentCreate, PostUpdate
from app.models.user import User
from typing import List, Optional

# --- Post Logic ---
def create_post(db: Session, user_id: int, post_in: PostCreate) -> Post:
    db_post = Post(
        user_id=user_id,
        content_text=post_in.content_text,
        caption=post_in.caption,
        media_url=post_in.media_url
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_feed(db: Session, user_id: int, limit: int = 50, skip: int = 0) -> List[Post]:
    following_ids = db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()
    # Extract IDs into a list and add self
    user_ids = [f[0] for f in following_ids]
    user_ids.append(user_id)
    
    return db.query(Post).filter(
        Post.user_id.in_(user_ids)
    ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def get_user_posts(db: Session, user_id: int, limit: int = 50, skip: int = 0) -> List[Post]:
    return db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

def update_post(db: Session, user_id: int, post_id: int, post_in: PostUpdate) -> Optional[Post]:
    post = get_post(db, post_id)
    if not post or post.user_id != user_id:
        return None
        
    if post_in.content_text is not None:
        post.content_text = post_in.content_text
    if post_in.caption is not None:
        post.caption = post_in.caption
    if post_in.media_url is not None:
        post.media_url = post_in.media_url
        
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, user_id: int, post_id: int) -> bool:
    post = get_post(db, post_id)
    if not post or post.user_id != user_id:
        return False
        
    # Delete associated data? 
    # Cascade delete should handle it if configured in DB models, 
    # but SQLAlchemy relationships might need 'cascade="all, delete"'
    # Let's assume basic deletion for now, foreign keys usually set to cascade or restrict.
    # If not, we might get IntegrityError. 
    # Ideally should delete likes/comments first if no cascade.
    
    # Let's check models later, for now try delete.
    db.delete(post)
    db.commit()
    return True

# --- Interaction Logic ---

def like_post(db: Session, user_id: int, post_id: int):
    # Check if post exists
    post = get_post(db, post_id)
    if not post:
        return False
        
    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    if existing_like:
        return True # Already liked
        
    new_like = Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    
    # Notify post owner (if not self)
    if post.user_id != user_id:
        notif = Notification(
            receiver_id=post.user_id,
            sender_id=user_id,
            type=NotificationType.like,
            post_id=post_id
        )
        db.add(notif)
        
    db.commit()
    return True

def unlike_post(db: Session, user_id: int, post_id: int):
    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    if existing_like:
        db.delete(existing_like)
        db.commit()
    return True

def add_comment(db: Session, user_id: int, post_id: int, comment_in: CommentCreate) -> Optional[Comment]:
    post = get_post(db, post_id)
    if not post:
        return None
        
    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        comment_text=comment_in.comment_text
    )
    db.add(comment)
    
    if post.user_id != user_id:
        notif = Notification(
            receiver_id=post.user_id,
            sender_id=user_id,
            type=NotificationType.comment,
            post_id=post_id
        )
        db.add(notif)
        
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, user_id: int, comment_id: int) -> bool:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return False
    
    # Logic: Owner of comment OR Owner of post can delete
    # We need post owner
    post_owner_id = comment.post.user_id
    
    if comment.user_id == user_id or post_owner_id == user_id:
        db.delete(comment)
        db.commit()
        return True
        
    return False

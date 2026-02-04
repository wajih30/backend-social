from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.api.auth import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserPublic
from app.schemas.social import (
    PostCreate, 
    Post as PostSchema, 
    CommentCreate, 
    Comment as CommentSchema, 
    PostUpdate, 
    PostDetail
)
from app.services import post_service, social_service

router = APIRouter()

# --- Posts ---
@router.post("/", response_model=PostSchema)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return post_service.create_post(db, current_user.id, post_in)

@router.put("/{post_id}", response_model=PostSchema)
def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = post_service.update_post(db, current_user.id, post_id, post_in)
    if not post:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post or post not found")
    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = post_service.delete_post(db, current_user.id, post_id)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post or post not found")
    return {"message": "Post deleted successfully"}

@router.get("/feed", response_model=List[PostSchema])
def read_feed(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posts = post_service.get_feed(db, current_user.id, limit, skip)
    # Populate calculated fields (likes_count, comments_count, is_liked_by_me)
    # Ideally done in service with efficient queries, but for now:
    for p in posts:
        p.likes_count = len(p.likes)
        p.comments_count = len(p.comments)
        p.is_liked_by_me = any(l.user_id == current_user.id for l in p.likes)
    return posts



@router.get("/{post_id}", response_model=PostDetail)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = post_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Populate calculated fields
    post.likes_count = len(post.likes)
    post.comments_count = len(post.comments)
    post.is_liked_by_me = any(l.user_id == current_user.id for l in post.likes)
    
    # Ensure comments are loaded and have user info (lazy loading should work, but for safety)
    # The Comment schema requires 'user', so it must be populated
    
    return post



@router.get("/user/{user_id}", response_model=List[PostSchema])
def read_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Auth optional for public? Spec says "Authenticated users can create posts", implies viewing is open? Requirement says "View other users profiles -> Display user's posts". 
    # Let's keep it authenticated for consistency with "Social Media" usually requiring account for feed/details
):
    posts = post_service.get_user_posts(db, user_id, limit, skip)
    for p in posts:
        p.likes_count = len(p.likes)
        p.comments_count = len(p.comments)
        p.is_liked_by_me = any(l.user_id == current_user.id for l in p.likes)
    return posts


# --- Follows ---
@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = social_service.follow_user(db, current_user.id, user_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cannot follow user (self or already followed)")
    return {"message": "Followed successfully"}

@router.delete("/{user_id}/follow")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = social_service.unfollow_user(db, current_user.id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {"message": "Unfollowed successfully"}

@router.get("/{user_id}/followers", response_model=List[UserPublic])
def get_user_followers(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return social_service.get_followers(db, user_id)

@router.get("/{user_id}/following", response_model=List[UserPublic])
def get_user_following(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return social_service.get_following(db, user_id)

# --- Interactions ---
@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not post_service.like_post(db, current_user.id, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post liked"}

@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_service.unlike_post(db, current_user.id, post_id)
    return {"message": "Post unliked"}

@router.post("/{post_id}/comment", response_model=CommentSchema)
def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = post_service.add_comment(db, current_user.id, post_id, comment_in)
    if not comment:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Populate user for response
    comment.user = current_user
    return comment

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = post_service.delete_comment(db, current_user.id, comment_id)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment or comment not found")
    return {"message": "Comment deleted"}

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    is_email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    # Followers: Users who follow this user
    followers = relationship(
        "Follow", 
        foreign_keys="[Follow.following_id]",
        backref="following_user"
    )
    # Following: Users this user follows
    following = relationship(
        "Follow", 
        foreign_keys="[Follow.follower_id]",
        backref="follower_user"
    )

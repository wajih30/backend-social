from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class UserInDBBase(UserBase):
    id: int
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserPublic(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    followers_count: int = 0
    following_count: int = 0

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

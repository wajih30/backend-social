from sqlalchemy.orm import Session
from app.models.user import User
from app.models.otp import OTPPurpose
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.services import otp_service, user_service, email_service
from app.core.config import settings
from jose import jwt, JWTError
from app.schemas.user import TokenPayload
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException

def refresh_access_token(db: Session, refresh_token: str) -> Optional[Dict[str, str]]:
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if payload.get("type") != "refresh":
            return None
    except (JWTError, Exception):
        return None
    
    user = user_service.get(db, token_data.sub)
    if not user:
        return None
        
    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

def forgot_password(db: Session, email: str) -> None:
    user = user_service.get_by_email(db, email)
    if not user:
        
        raise HTTPException(status_code=404, detail="User with this email not found.")
    
    otp = otp_service.create_otp(db, email, OTPPurpose.password_reset)
    if not email_service.send_otp_email(email, otp):
        
        raise HTTPException(status_code=500, detail="Failed to send reset email. Please check your SMTP settings.")

def reset_password(db: Session, email: str, otp: str, new_password: str) -> None:
    # Validate complexity first so we don't 'burn' the OTP if the password is weak
    error = user_service.validate_password_complexity(new_password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    if not otp_service.verify_otp(db, email, otp, OTPPurpose.password_reset):
        raise HTTPException(status_code=400, detail="Invalid or expired reset code.")
        
    user = user_service.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")
        
    user.password_hash = get_password_hash(new_password)
    db.commit()

def register_user(db: Session, user_in: UserCreate) -> User:
    # Validation is done in API or service before calling this usually, 
    # but we can double check or just proceed with creation.
    # The API layer checks for existence now, or we can move it here.
    # Let's move existence check here for safety? 
    # The user asked to move DB interactions.
    
    if user_service.get_by_email(db, user_in.email):
        
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    if user_service.get_by_username(db, user_in.username):
        
        raise HTTPException(status_code=400, detail="User with this username already exists.")

    # Validate complexity
    error = user_service.validate_password_complexity(user_in.password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Log debug info
    print(f"DEBUG: Hashing password type={type(user_in.password)} val={repr(user_in.password)}")
    
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_email_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate OTP
    otp = otp_service.create_otp(db, db_user.email, OTPPurpose.registration)
    
    # Send OTP via Email
    if not email_service.send_otp_email(db_user.email, otp):
       
        # We don't necessarily want to fail registration if email fails, 
        # but the user needs the OTP to verify. 
        # So we should probably indicate an error.
        raise HTTPException(status_code=500, detail="User created but failed to send verification email. Please contact support.")
    
    return db_user

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    user = user_service.get_by_username(db, username_or_email)
    if not user:
        # Try case-insensitive email lookup
        user = user_service.get_by_email(db, username_or_email)
        
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None
        
    return user


def verify_registration(db: Session, email: str, otp: str) -> bool:
    if otp_service.verify_otp(db, email, otp, OTPPurpose.registration):
        user = user_service.get_by_email(db, email)
        if user:
            user.is_email_verified = True
            db.commit()
            return True
    return False

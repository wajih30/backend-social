from sqlalchemy.orm import Session
from app.models.user import User
from app.models.otp import OTPPurpose
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from app.services import otp_service, user_service, email_service
from typing import Optional

def register_user(db: Session, user_in: UserCreate) -> User:
    # Validation is done in API or service before calling this usually, 
    # but we can double check or just proceed with creation.
    # The API layer checks for existence now, or we can move it here.
    # Let's move existence check here for safety? 
    # The user asked to move DB interactions.
    
    existing_email = user_service.get_by_email(db, user_in.email)
    existing_username = user_service.get_by_username(db, user_in.username)
    if existing_email or existing_username:
        return None # Indicate failure or raise exception? Returning None lets API handle 400.

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
    email_service.send_otp_email(db_user.email, otp)
    
    return db_user

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    user = user_service.get_by_username(db, username_or_email)
    if not user:
        # Try case-insensitive email lookup
        user = user_service.get_by_email(db, username_or_email)
        
    if not user:
        print(f"DEBUG: User search failed for input: '{username_or_email}'")
        return None


        
    if not verify_password(password, user.password_hash):
        print(f"DEBUG: Login failed for {username_or_email}")
        print(f"DEBUG: Password provided length: {len(password)}")
        print(f"DEBUG: Stored Hash: {user.password_hash}")
        # Test verification explicitly again
        is_valid = verify_password(password, user.password_hash)
        print(f"DEBUG: Re-verification result: {is_valid}")
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

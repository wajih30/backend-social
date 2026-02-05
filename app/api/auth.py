from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, create_refresh_token
from app.api.deps import get_db, get_current_user
from app.services import auth_service
from app.schemas.user import (
    UserCreate, 
    User as UserSchema, 
    Token, 
    OTPVerify, 
    ForgotPasswordRequest, 
    ResetPasswordRequest
)

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, user_in)

@router.post("/verify-otp")
def verify_registration_otp(data: OTPVerify, db: Session = Depends(get_db)):
    if auth_service.verify_registration(db, data.email, data.otp):
        return {"message": "Email verified successfully"}
    
    raise HTTPException(status_code=400, detail="Invalid or expired OTP")

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    tokens = auth_service.refresh_access_token(db, refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
        )
    return tokens

# --- Password Reset ---

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.forgot_password(db, data.email)
    return {"message": "If the email exists, an OTP has been sent."}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service.reset_password(db, data.email, data.otp, data.new_password)
    return {"message": "Password reset successfully"}

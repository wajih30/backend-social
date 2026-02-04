import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp import EmailOTP, OTPPurpose
from app.core.security import get_password_hash, verify_password

def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

def create_otp(db: Session, email: str, purpose: OTPPurpose) -> str:
    otp_code = generate_otp()
    otp_hash = get_password_hash(otp_code)
    
    # Set expiration (e.g., 10 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    db_otp = EmailOTP(
        email=email,
        otp_hash=otp_hash,
        purpose=purpose,
        expires_at=expires_at
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return otp_code

def verify_otp(db: Session, email: str, otp_code: str, purpose: OTPPurpose) -> bool:
    db_otp = db.query(EmailOTP).filter(
        EmailOTP.email == email,
        EmailOTP.purpose == purpose,
        EmailOTP.is_used == False,
        EmailOTP.expires_at > datetime.utcnow()
    ).order_by(EmailOTP.created_at.desc()).first()
    
    if not db_otp:
        return False
    
    if verify_password(otp_code, db_otp.otp_hash):
        db_otp.is_used = True
        db.commit()
        return True
    
    return False

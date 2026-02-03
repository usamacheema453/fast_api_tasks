from fastapi import APIRouter, HTTPException, Depends, Request
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.core.dependencies import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.refresh_token import RefreshToken
from app.models.token_blackklist import TokenBlacklist
from app.models.login_session import LoginSession
from app.core.mailer import send_email, login_alert_email
from app.config import ADMIN_EMAIL

router = APIRouter()

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    exist_user = db.query(User).filter(User.email == email).first()

    if exist_user:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User Registered Successfully"}

@router.post("/login")
def login(email: str, password: str, request: Request, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return {"error": "Invalid Credentials"}
    
    access_token = create_access_token(
        {"user_id": user.id, "role": user.role},
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

    refresh_token = create_refresh_token()

    db_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    session = LoginSession(
        user_id = user.id,
        ip_address = request.client.host,
        user_agent = request.headers.get("user-agent")
    )

    subject, body = login_alert_email(
        user.email,
        request.client.host,
        request.headers.get("user-agent")
    )

    send_email(
        to_email=ADMIN_EMAIL,
        subject=subject,
        body=body
    )


    db.add(db_token)
    db.add(session)
    db.commit()

    return{
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):

    token_entry = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not token_entry:
        return {"error": "Invalid refresh token"}

    if token_entry.expires_at < datetime.utcnow():
        return {"error": "Refresh token expired"}

    new_access = create_access_token(
        {"user_id": token_entry.user_id},
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return {"access_token": new_access}


@router.post("/logout")
def logout(access_token: str, db: Session = Depends(get_db)):
    revoked = TokenBlacklist(token= access_token)
    db.add(revoked)
    db.commit()
    return { "message": "logout"}
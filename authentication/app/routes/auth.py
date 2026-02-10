from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ADMIN_EMAIL
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.dependencies import get_db, get_current_user, get_bearer_token
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.token_blackklist import TokenBlacklist
from app.models.login_session import LoginSession
from app.core.mailer import send_email, login_alert_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    exist_user = db.query(User).filter(User.email == email).first()
    if exist_user:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(email=email, password=hash_password(password), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(
    email: str,
    password: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {"user_id": user.id, "role": user.role},
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_token = create_refresh_token()
    db_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    session = LoginSession(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    db.add(db_token)
    db.add(session)
    db.commit()

    subject, body = login_alert_email(
        user.email,
        request.client.host,
        request.headers.get("user-agent") or "",
    )

    if ADMIN_EMAIL:
        background_tasks.add_task(send_email, ADMIN_EMAIL, subject, body)

    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    new_access = create_access_token(
        {"user_id": token_entry.user_id, "role": "user"},
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": new_access}

@router.post("/logout")
def logout(
    token: str = Depends(get_bearer_token),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    revoked = TokenBlacklist(token=token)
    db.add(revoked)
    db.commit()
    return {"message": "Logged out"}

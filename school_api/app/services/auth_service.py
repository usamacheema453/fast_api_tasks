import datetime
from sqlalchemy.orm import Session
from app.core.security import (
    verify_password,
    create_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token_value,
    decode_token
)
from app.core.config import settings
from app.models.user import User
from app.models.role import Role
from app.models.refresh_token import RefreshToken

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def register_user(db: Session, full_name: str, email: str, password: str, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).first()

    if not role:
        raise ValueError("Role does not exist")
    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("User with this email already exists")
    
    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        role_id=role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def issue_token(db: Session, user: User) -> tuple[str,str]:

    access_payload = {
        "sub": str(user.id),
        "role": user.role.name,
    }
    access_token = create_access_token(access_payload)

    refresh_value = new_refresh_token_value()
    refresh_hashed = hash_refresh_token(refresh_value)

    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=settings.REFRESH_TOKEN)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hashed,
        expires_at=expires_at,
        revoked=False
    )
    db.add(db_token)
    db.commit()
    
    return access_token, refresh_value

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
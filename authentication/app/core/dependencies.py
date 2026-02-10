from typing import Generator, Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decode_token
from app.models.token_blacklist import TokenBlacklist

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_bearer_token(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    return authorization[len(prefix):].strip()

def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> dict:
    revoked = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if revoked:
        raise HTTPException(status_code=401, detail="Token revoked")

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(role: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return checker

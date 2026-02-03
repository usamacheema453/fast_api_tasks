import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.auth import RegisterIn, Login, TokenOut
from app.services.auth_service import register_user, get_user_by_email, issue_token, authenticate_user
from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    try:
        user = register_user(
            db,
            full_name=data.full_name,
            email=data.email,
            password=data.password,
            role_name=data.role_name
        )
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post("/login", response_model=TokenOut)
def login(data: Login, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token, refresh_token = issue_token(db, user)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenOut)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(refresh_token)
    
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if db_token.expires_at < datetime.datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    
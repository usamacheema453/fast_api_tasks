from app.database import SessionLocal
import jwt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.token_blackklist import TokenBlacklist
from app.config import SECRET_KEY, ALGORITHM
from fastapi import HTTPException, Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session = Depends(SessionLocal)):
    blackListed = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()

    if blackListed:
        raise HTTPException(401, "Token revoked")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(401, "Invalid token")
    
def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(403, "Permission denied")
        return user
    return role_checker

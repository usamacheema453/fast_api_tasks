from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def require_role(allowed_roles: list[str]):
    def checker(current_user: User = Depends(get_current_user)):
       if current_user.role.name not in allowed_roles:
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
       return
    return checker

def require_permission(permission_name: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        code = {p.code for p in current_user.role.permissions}
        if permission_name not in code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return current_user
    return checker
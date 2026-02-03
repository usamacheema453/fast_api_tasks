import datetime
import hashlib
import secrets
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITM="HS256"

def hash_password(password: str) -> str:
    return pwt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwt_context.verify(plain_password, hashed_password)

def create_access_token(payload: dict) -> str:
    to_encode = payload.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITM])

def new_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
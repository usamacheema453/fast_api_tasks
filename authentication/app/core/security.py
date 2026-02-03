import jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ALGORITHM
from passlib.context import CryptContext
import uuid

def create_access_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

pwt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwt_context.hash(password)

def verify_password(password, hashed):
    return pwt_context.verify(password, hashed)

def create_refresh_token():
    return str(uuid.uuid4())
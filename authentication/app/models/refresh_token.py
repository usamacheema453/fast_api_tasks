from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id= Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime,default=datetime.utcnow)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class LoginSession(Base):
    __tablename__ = "login_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
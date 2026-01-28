from sqlalchemy import Column, Integer, String
from app.database.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ ="users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

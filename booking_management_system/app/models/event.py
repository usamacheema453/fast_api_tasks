from sqlalchemy import Column, Integer, String, DateTime
from app.database.base import Base
import datetime
from sqlalchemy.orm import relationship

class Event(Base):
    __tablename__ ="events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    location = Column(String, index=True, nullable=False)
    total_seats = Column(Integer, nullable=False)
    event_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")
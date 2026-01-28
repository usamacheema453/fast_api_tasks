from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
import datetime
 
class Booking_status:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    status = Column(String, default=Booking_status.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
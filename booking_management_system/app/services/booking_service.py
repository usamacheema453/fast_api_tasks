from sqlalchemy.orm import Session, joinedload
from app.models.booking import Booking
from app.database.db import get_db
from app.models.event import Event 
def create_booking(db: Session, user_id: int, event_id: int) -> Booking:
    total_bookings = db.query(Booking).filter(Booking.event_id == event_id,
                                              Booking.status != "canceled").count()
    
    if total_bookings >=5:
        return None  # Indicate that booking cannot be created due to full capacity
    seats_full = db.query(Event).filter(Event.id == event_id).first()
    if seats_full and total_bookings >= seats_full.total_seats:
        return None  # Indicate that booking cannot be created due to full capacity
    booking = Booking(user_id=user_id, event_id=event_id, status="confirmed")
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_bookings_by_id(db: Session = get_db(), booking_id: int = None):
    if booking_id:
        return db.query(Booking).options(joinedload(Booking.user), joinedload(Booking.event)).filter(Booking.id == booking_id).first()
    
def update_booking_status(db: Session, booking_id: int, user_id: int, new_status: str) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user_id).first()
    if not booking:
        return None  # Booking not found or does not belong to user
    booking.status = new_status
    db.commit()
    db.refresh(booking)
    return booking

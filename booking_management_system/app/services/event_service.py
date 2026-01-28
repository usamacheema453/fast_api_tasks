from sqlalchemy.orm import Session
from app.models.event import Event

def create_event(db: Session, title: str, location: str, total_seats: int):
    event = Event(title=title, location=location, total_seats=total_seats)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def update_event(db: Session, event_id: int, date: str = None, location: str = None, total_seats: int = None):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None  # Event not found
    if date:
        event.event_date = date
    if location:
        event.location = location
    if total_seats:
        event.total_seats = total_seats
    db.commit()
    db.refresh(event)
    return event
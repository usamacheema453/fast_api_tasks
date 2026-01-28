from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.event import EventCreate
from app.services.event_service import create_event, update_event

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", status_code=201)
def create_new_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = create_event(db, event.title, event.location, event.total_seats)
    return new_event

@router.put("/{event_id}/", status_code=200)
def update_event_details(db: Session= Depends(get_db), event_id: int = None, date: str = None, location: str = None, total_seats: int = None):
    updated_event = update_event(db, event_id, date, location, total_seats)
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    return updated_event
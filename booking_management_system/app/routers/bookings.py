from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.booking import BookingCreate
from app.services.booking_service import create_booking, get_bookings_by_id, update_booking_status

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", status_code=201)
def book_ticket(booking: BookingCreate, db: Session = Depends(get_db)):
    booking= create_booking(db, booking.user_id, booking.event_id)
    if booking is None:
        raise HTTPException(status_code=400, detail="Booking cannot be created. Event may be at full capacity.")
    return booking

@router.get("/id/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = get_bookings_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking

@router.put("/update_status/", status_code=200)
def change_status(booking_id: int, user_id: int, new_status: str, db: Session = Depends(get_db)):
    booking = update_booking_status(db, booking_id, user_id, new_status)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found or does not belong to user.")
    return booking
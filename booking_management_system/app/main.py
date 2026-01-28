from fastapi import FastAPI
from app.routers import  bookings, users, event
from app.database.session import engine
from app.database.base import Base
import app.models

app = FastAPI(title="Booking Management System")

Base.metadata.create_all(bind=engine)
app.include_router(bookings.router)
app.include_router(users.router)
app.include_router(event.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Management System API"}
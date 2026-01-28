from pydantic import BaseModel

class EventCreate(BaseModel):
    title: str
    location: str
    total_seats: int

class EventResponse(BaseModel):
    title: str
    location: str

    class Config:
        orm_mode = True
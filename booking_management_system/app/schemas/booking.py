from pydantic import BaseModel
from app.schemas.event import EventResponse
from app.schemas.user import UserResponse
class BookingCreate(BaseModel):
    user_id: int
    event_id: int

class BookingResponse(BaseModel):
    id: int
    user: UserResponse
    event: EventResponse
    status: str

    class Config:
        orm_mode = True
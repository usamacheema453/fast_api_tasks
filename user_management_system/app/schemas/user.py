from pydantic import BaseModel
from typing import List, Optional
from app.schemas.Task import TaskResponse
class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]= None
    address: Optional[str] = None
    tasks: List[TaskResponse] = []

    class Config:
        orm_mode = True
from pydantic import BaseModel
from typing import List
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
    phone: str
    address: str
    tasks: List[TaskResponse] = []
    
    class Config:
        orm_mode = True
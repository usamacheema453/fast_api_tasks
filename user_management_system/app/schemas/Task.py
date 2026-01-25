from pydantic import BaseModel
from typing import Optional, List

class TaskCreate(BaseModel):
    title: str

class TaskResponse(TaskCreate):
    id: int
    class Config:
        orm_mode = True
    

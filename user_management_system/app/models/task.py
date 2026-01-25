from app.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "tasks"

    id= Column(Integer, primary_key=True)
    title= Column(String, nullable=False, index=True)
    user_id= Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tasks")
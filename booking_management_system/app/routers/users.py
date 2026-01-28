from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_all_users

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(db, user.name, user.email)
    if new_user is None:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    return new_user

@router.get("/", status_code=200)
def get_all_data(db: Session = Depends(get_db)):
    users = get_all_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No users found.")
    return users
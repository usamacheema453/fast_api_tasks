from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.user import create_user, delete_user, update_user, get_users
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.database.database import SessionLocal, Base, engine
from typing import List
from app.crud.task import create_task, get_tasks_for_user
from app.schemas.Task import TaskCreate, TaskResponse
from app.models.task import Task

app= FastAPI()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserResponse)
def add_user(users:UserCreate, db: Session=Depends(get_db)):
    return create_user(db=db, user=users)

@app.get("/users/", response_model=List[UserResponse])
def fetch_users(db: Session = Depends(get_db)):
    return get_users(db=db)

@app.put("/users/{user_id}", response_model=UserResponse)
def put_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = update_user(db=db, user_id=user_id, user=user)
    if db_user:
        return db_user
    raise HTTPException(status_code=404, detail="User Not found")

@app.delete("/user/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    db_users = delete_user(db=db, user_id=user_id)
    if db_users:
        return {"message" : "Deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

## Task User

@app.post("/post", response_model=TaskResponse)
def add_task(
    user_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    return create_task(db=db, user_id=user_id, task=task)


@app.get("/", response_model=List[TaskResponse])
def fetch_task(user_id: int, db: Session = Depends(get_db)):
    return get_tasks_for_user(db=db, user_id=user_id)

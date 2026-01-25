from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.Task import TaskCreate, TaskResponse

def create_task(db: Session, user_id: int, task: TaskCreate):
    new_task = Task(
        title= task.title,
        user_id=user_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_tasks_for_user(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id).all()


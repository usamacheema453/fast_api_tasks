from sqlalchemy.orm import Session
from app.models.user import User

def create_user(db: Session, name: str, email: str) -> User:
    user_exists = db.query(User).filter(User.email == email).first()
    if user_exists:
        return None  # Return existing user if email already registered
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).all()
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


DATABASE_URL = "postgresql://postgres:123123@localhost:5433/event_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
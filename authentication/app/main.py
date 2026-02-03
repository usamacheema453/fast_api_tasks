from fastapi import FastAPI
from app.database import Base, engine
from app.models import user
from app.routes.auth import router as auth_router
from app.middleware.rate_limit import rate_limiter
from app.core.logger import setup_logger

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

logger = setup_logger()
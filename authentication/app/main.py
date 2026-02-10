from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import setup_logger
from app.database import Base, engine

from app.middleware.rate_limit import rate_limiter
from app.middleware.security_headers import security_headers
from app.middleware.logger_middleware import log_requests

from app.routes.auth import router as auth_router
from app.config import CORS_ORIGINS

logger = setup_logger()

app = FastAPI(title="Secure API")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def middleware_security_headers(request, call_next):
    return await security_headers(request, call_next)

@app.middleware("http")
async def middleware_rate_limit(request, call_next):
    return await rate_limiter(request, call_next)

@app.middleware("http")
async def middleware_logger(request, call_next):
    return await log_requests(request, call_next, logger)

app.include_router(auth_router)

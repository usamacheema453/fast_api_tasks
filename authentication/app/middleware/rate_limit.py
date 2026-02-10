import time
from fastapi import Request
from fastapi.responses import JSONResponse
from app.config import RATE_LIMIT_WINDOW_SECONDS, RATE_LIMIT_MAX_REQUESTS

_requests: dict[str, list[float]] = {}

async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    timestamps = _requests.get(ip, [])
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    timestamps = [t for t in timestamps if t >= window_start]

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
        )

    timestamps.append(now)
    _requests[ip] = timestamps

    return await call_next(request)

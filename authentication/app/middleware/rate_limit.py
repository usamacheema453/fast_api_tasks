import time

from fastapi import Request, HTTPException

requests = {}

async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    if ip not in request:
        request[ip] = []
    
    request[ip] = [t for t in request[ip] if now - t < 60]

    if len(request[ip] > 20):
        raise HTTPException(429, "To many request")
    
    requests[ip].append(now)
    return await call_next(request)
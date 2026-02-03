from fastapi import Request
import time
from app.main import logger

async def log_requests(request: Request, call_next):
    start_time= time.time()

    try:
        response = await call_next(request)

        logger.info(
            f"{request.method} {request.url.path}"
            f"Status={response.status_code}"
            f"Time={time.time() - start_time:.2f}s"
            f"IP={request.client.host}"
        )

        return response
    
    except Exception as e:
        logger.error(
            f"Error {request.method} {request.url.path}"
            f"IP={request.client.host}"
            f"Error={str(e)}"
        )
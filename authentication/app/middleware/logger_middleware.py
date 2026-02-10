from fastapi import Request
import time
import uuid
from logging import Logger

async def log_requests(request: Request, call_next, logger: Logger):
    request_id = str(uuid.uuid4)
    start_time = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            f"request_id={request_id}"
            f"method={request.method} path={request.url.path}"
            f"status={response.status_code}"
            f"duration={duration:.3f}s ip={request.client.host}"
        )

        response.headers["x-Request-Id"] = request_id
        return response

    except Exception as exc:
        duration = time.time() - start_time
        logger.exception(
            f"request_id={request_id} "
            f"method={request.method} path={request.url.path} "
            f"duration={duration:.3f}s ip={request.client.host} "
            f"error={str(exc)}"
        )
        raise
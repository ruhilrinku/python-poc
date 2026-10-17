import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log one structured line per request with method, path, status and latency."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        base_fields = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }
        logger.info("request.start", extra={"extra_fields": base_fields})

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request.failed",
                extra={"extra_fields": {**base_fields, "duration_ms": duration_ms}},
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request.completed",
            extra={
                "extra_fields": {
                    **base_fields,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            },
        )
        response.headers["x-request-id"] = request_id
        return response

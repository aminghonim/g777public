import time
import logging
from datetime import datetime, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured Security Logger (ASVS V3)
logger = logging.getLogger("security_logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    # Log with context in JSON-like structure
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": "%(message)s", "context": %(context)s}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_security_event(event_msg: str, level: int = logging.INFO, **context):
    """Local helper to inject UTC timestamp and context dictionaries."""
    utc_now = datetime.now(timezone.utc).isoformat()
    extra_context = {"context": context, "asctime": utc_now}
    logger.log(level, event_msg, extra=extra_context)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Avoid logging raw payload implicitly to protect PII; log metadata only.
        log_security_event(
            "Incoming Request",
            method=request.method,
            url=str(request.url.path),
            client_ip=request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)

            # ASVS V16: Add strict Security Headers
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; frame-ancestors 'none';"
            )
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"

            # Log failed auth/authz attempts based on status code
            if response.status_code in (401, 403):
                log_security_event(
                    "Failed Authentication/Authorization Attempt",
                    level=logging.WARNING,
                    method=request.method,
                    url=str(request.url.path),
                    status_code=response.status_code,
                    client_ip=request.client.host if request.client else "unknown",
                )

            return response

        except Exception as e:
            # Log unexpected server errors
            log_security_event(
                "Unexpected Error Processing Request",
                level=logging.ERROR,
                error=str(e),
                method=request.method,
                url=str(request.url.path),
                client_ip=request.client.host if request.client else "unknown",
            )
            raise

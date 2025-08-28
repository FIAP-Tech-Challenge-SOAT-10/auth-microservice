import logging
import sys
from logging import getLogger, StreamHandler
from logging.config import dictConfig

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def configure_logging(level: str = "INFO", json_logs: bool = False):
    log_level = level.upper()
    if json_logs:
        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                        "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                    }
                },
                "handlers": {
                    "json": {
                        "class": "logging.StreamHandler",
                        "formatter": "json",
                        "stream": sys.stdout,
                    }
                },
                "loggers": {
                    "uvicorn": {"handlers": ["json"], "level": log_level},
                    "src": {"handlers": ["json"], "level": log_level},
                },
            }
        )
    else:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[StreamHandler(sys.stdout)],
        )


def get_logger(name: str) -> logging.Logger:
    return getLogger(name)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = get_logger(__name__)
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response

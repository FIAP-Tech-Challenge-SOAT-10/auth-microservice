import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.config import settings
from src.logging_config import LoggingMiddleware, configure_logging, get_logger
from src.infrastructure.monitoring.metrics import setup_metrics # Updated import
from src.api.routers import admin, auth, health

# Configure logging
configure_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=os.getenv("JSON_LOGS", "true").lower() == "true",
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    logger.info("Starting authentication microservice")
    yield
    # Shutdown
    logger.info("Shutting down authentication microservice")


app = FastAPI(
    title="Authentication Microservice",
    description="A FastAPI-based authentication microservice with monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure Prometheus metrics
instrumentator = setup_metrics()
instrumentator.instrument(app)

# Add logging middleware
# app.add_middleware(LoggingMiddleware) # Keep commented for now, as it might interfere with logging setup

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])


@app.get("/")
async def root() -> dict[str, str]:
    # logger.info("Root endpoint accessed")
    return {"message": "Authentication Microservice is running"}


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
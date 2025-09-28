import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.api.routers import admin, auth, health
from src.config import settings
from src.infrastructure.monitoring.metrics import setup_metrics  # Updated import
from src.logging_config import configure_logging, get_logger

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
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Authentication operations including signup, login, logout, and profile management",
        },
        {
            "name": "admin",
            "description": "Administrative operations requiring admin role",
        },
        {
            "name": "health",
            "description": "Health check endpoints for monitoring",
        },
    ],
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Authentication Microservice",
        version="1.0.0",
        description="A FastAPI-based authentication microservice with monitoring",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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

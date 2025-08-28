import time
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import get_db

router = APIRouter()


async def check_database_health(db: AsyncSession) -> dict[str, Any]:
    """Check database connectivity and basic operations."""
    try:
        start_time = time.time()
        # Simple query to test database connectivity
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        response_time = time.time() - start_time

        return {
            "status": "healthy",
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "authentication-microservice",
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Detailed health check including database connectivity."""

    # Check database health
    db_health = await check_database_health(db)

    # Overall health status
    overall_status = "healthy" if db_health["status"] == "healthy" else "unhealthy"

    health_data = {
        "status": overall_status,
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "authentication-microservice",
        "version": "1.0.0",
        "checks": {"database": db_health},
    }

    # Return 503 if any check fails
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=health_data)

    return health_data


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Kubernetes readiness probe endpoint."""
    try:
        # Check if we can connect to database
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail={"status": "not ready"}) from None


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


@router.get("/health/startup")
async def startup_check() -> dict[str, str]:
    """Kubernetes startup probe endpoint."""
    # In a real app, you might check for cold-start conditions
    return {"status": "startup complete"}
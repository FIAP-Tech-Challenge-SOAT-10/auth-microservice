from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import require_role
from src.infrastructure.database.models.refresh_token import RefreshToken
from src.infrastructure.database.models.roles import UserRole
from src.infrastructure.database.models.user import User
from src.infrastructure.database.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/dashboard",
    summary="Get admin dashboard",
    description="Get admin dashboard with system statistics. Requires admin role for access.",
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied. Admin role required"},
    },
)
async def get_admin_dashboard(
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """
    Get admin dashboard with system statistics.

    Requires admin role for access.

    Returns:
        dict: Dashboard data with user and system statistics
    """
    # Get user statistics
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()

    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active.is_(True))
    )
    active_users = active_users_result.scalar()

    admin_users_result = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.ADMIN)
    )
    admin_users = admin_users_result.scalar()

    # Get refresh token statistics
    active_sessions_result = await db.execute(
        select(func.count(RefreshToken.id)).where(RefreshToken.is_active.is_(True))
    )
    active_sessions = active_sessions_result.scalar()

    return {
        "message": f"Welcome to the admin dashboard, {current_admin.username}!",
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "active_sessions": active_sessions,
        },
        "admin_user": current_admin.username,
    }


@router.get("/users")
async def list_users(
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of all users (admin only).

    Requires admin role for access.

    Returns:
        dict: List of users with basic information
    """
    result = await db.execute(
        select(
            User.id,
            User.username,
            User.email,
            User.full_name,
            User.role,
            User.is_active,
            User.created_at,
        )
    )
    users = result.all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at,
            }
            for user in users
        ],
        "total_count": len(users),
    }

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.auth import (
    RefreshTokenRequest,
    Token,
    TokenWithRefresh,
)
from src.api.schemas.user import UserCreate, UserLogin
from src.api.schemas.user import UserResponse
from src.infrastructure.database.models.refresh_token import RefreshToken
from src.infrastructure.database.models.user import User
from src.infrastructure.database.session import get_db
from src.infrastructure.security.password_service import (
    get_password_hash,
    verify_password,
)
from src.infrastructure.security.token_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_token_hash,
    verify_refresh_token,
)

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.
    """
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )


@router.post("/login", response_model=TokenWithRefresh)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT access token and refresh token.
    """
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "email": user.email,
            "user_id": user.id,
            "role": user.role.value,
        }
    )

    refresh_token, jti = create_refresh_token(user.id)
    refresh_token_hash = generate_token_hash(refresh_token)

    expires_at = datetime.now(UTC) + timedelta(days=7)
    db_refresh_token = RefreshToken(
        jti=jti,
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
    )

    db.add(db_refresh_token)
    await db.commit()

    return TokenWithRefresh(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh(refresh_request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using a valid refresh token.
    """
    try:
        payload = decode_refresh_token(refresh_request.refresh_token)
        user_id = int(payload.get("sub"))
        jti = payload.get("jti")

        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.jti == jti)
            .where(RefreshToken.is_active.is_(True))
            .where(RefreshToken.user_id == user_id)
        )
        db_refresh_token = result.scalar_one_or_none()

        if not db_refresh_token or not verify_refresh_token(
            refresh_request.refresh_token, db_refresh_token.token_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if db_refresh_token.expires_at.tzinfo is None:
            db_refresh_token.expires_at = db_refresh_token.expires_at.replace(tzinfo=UTC)

        if db_refresh_token.expires_at < datetime.now(UTC):
            db_refresh_token.is_active = False
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        db_refresh_token.is_active = False
        await db.commit()

        access_token = create_access_token(
            data={
                "sub": user.username,
                "email": user.email,
                "user_id": user.id,
                "role": user.role.value,
            }
        )

        return Token(access_token=access_token, token_type="bearer")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by revoking their refresh token.
    """
    try:
        payload = decode_refresh_token(refresh_request.refresh_token)
        jti = payload.get("jti")

        result = await db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti).where(RefreshToken.is_active.is_(True))
        )
        db_refresh_token = result.scalar_one_or_none()

        if db_refresh_token:
            db_refresh_token.is_active = False
            await db.commit()

        return {"message": "Successfully logged out"}

    except Exception:
        return {"message": "Successfully logged out"}
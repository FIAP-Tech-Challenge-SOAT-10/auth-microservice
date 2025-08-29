from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.auth import RefreshTokenRequest, Token, TokenWithRefresh
from src.api.schemas.user import UserCreate, UserLogin, UserResponse
from src.domain.use_cases.auth_service import AuthService
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.refresh_token_repository import RefreshTokenRepository # New import
from src.infrastructure.database.session import get_db
from src.infrastructure.database.models.user import User

router = APIRouter()

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    refresh_token_repo = RefreshTokenRepository(db) # New
    return AuthService(user_repo, refresh_token_repo) # Updated

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        new_user = await auth_service.register_user(
            username=user_data.username,
            full_name=user_data.full_name,
            cpf=user_data.cpf,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role.value if user_data.role else 'user',
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenWithRefresh)
async def login(
    credentials: UserLogin, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        tokens = await auth_service.authenticate_user(
            username=credentials.username, password=credentials.password
        )
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh(
    refresh_request: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        new_access_token = await auth_service.refresh_access_token(refresh_request.refresh_token)
        return new_access_token
    except ValueError as e: # Changed from NotImplementedError
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        await auth_service.logout_user(refresh_request.refresh_token)
        return {"message": "Successfully logged out"}
    except ValueError as e: # Changed from NotImplementedError
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
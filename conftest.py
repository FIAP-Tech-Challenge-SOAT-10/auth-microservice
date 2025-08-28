# """
# Pytest configuration and fixtures for the authentication microservice.
# """

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="function")
def client():
    """
    Simple test client for initial healthcheck tests.
    """
    with TestClient(app) as c:
        yield c


# @pytest.fixture(scope="function")
# def client():
#     """
#     Simple test client for initial healthcheck tests.
#     """
#     with TestClient(app) as c:
#         yield c

# import asyncio
# from collections.abc import AsyncGenerator, Generator

# import pytest
# import pytest_asyncio
# from fastapi.testclient import TestClient
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from sqlalchemy.pool import StaticPool

# from app.database import Base, get_db
# from app.main import app
# from models.refresh_token import RefreshToken  # type: ignore # noqa: F401

# Import models so they're registered with the Base metadata
# from models.user import User  # type: ignore # noqa: F401

# Test database URL - using SQLite in-memory for fast tests
# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async test engine
# test_engine = create_async_engine(
#     TEST_DATABASE_URL,
#     echo=False,
#     poolclass=StaticPool,
#     connect_args={
#         "check_same_thread": False,
#     },
# )

# Create async session factory for tests
# TestSessionLocal = async_sessionmaker(
#     test_engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False,
# )


# @pytest_asyncio.fixture(scope="function")
# async def test_db() -> AsyncGenerator[AsyncSession, None]:
#     """
#     Create a fresh database session for each test.
#     """
#     # Create all tables
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

#     # Create session
#     async with TestSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()

#     # Drop all tables after test
#     # async with test_engine.begin() as conn:
#     #     await conn.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture(scope="function")
# async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
#     """
#     Create a test client with dependency overrides.
#     """

#     async def get_test_db():
#         yield test_db

#     app.dependency_overrides[get_db] = get_test_db

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac

#     # Clean up
#     app.dependency_overrides.clear()


# @pytest.fixture(scope="function")
# def sync_client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
#     """
#     Create a synchronous test client for simpler tests.
#     """

#     async def get_test_db():
#         yield test_db

#     app.dependency_overrides[get_db] = get_test_db

#     with TestClient(app) as client:
#         yield client

#     # Clean up
#     app.dependency_overrides.clear()


# @pytest_asyncio.fixture
# async def test_user_data():
#     """
#     Sample user data for testing.
#     """
#     return {
#         "username": "testuser",
#         "email": "test@example.com",
#         "full_name": "Test User",
#         "password": "testpassword123",
#     }


# @pytest_asyncio.fixture
# async def created_user(client: AsyncClient, test_user_data: dict):
#     """
#     Create a test user and return the response.
#     """
#     response = await client.post("/api/v1/auth/signup", json=test_user_data)
#     assert response.status_code == 201
#     return response.json()


# @pytest_asyncio.fixture
# async def auth_token(client: AsyncClient, test_user_data: dict, created_user: dict):
#     """
#     Create a user and get an authentication token.
#     """
#     login_data = {
#         "username": test_user_data["username"],
#         "password": test_user_data["password"],
#     }
#     response = await client.post("/api/v1/auth/login", json=login_data)
#     assert response.status_code == 200
#     token_data = response.json()
#     return token_data["access_token"]


# @pytest.fixture(scope="session")
# def event_loop():
#     """
#     Create an instance of the default event loop for the test session.
#     """
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

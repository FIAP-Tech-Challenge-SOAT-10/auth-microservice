# Auth Microservice

A FastAPI-based authentication microservice with role-based authorization, PostgreSQL, SQLAlchemy 2.0 (async), and JWT authentication.

[![CI/CD Pipeline](https://img.shields.io/badge/CI_CD-Pipeline-black)](https://github.com/ju-c-lopes/auth-microservice/actions)
[![Coverage](https://codecov.io/gh/ju-c-lopes/auth-microservice/branch/main/graph/badge.svg)](https://codecov.io/gh/ju-c-lopes/auth-microservice)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Features

-   🚀 **FastAPI** with automatic API documentation
-   🗄️ **PostgreSQL** with async SQLAlchemy 2.0 via Docker Compose
-   🔐 **JWT-based authentication** with access and refresh tokens
-   👥 **Role-based authorization** (Admin/User roles)
-   📊 **Admin dashboard** with user management
-   🏗️ **Alembic database migrations**
-   🔧 **Connection pooling** and async database operations
-   ✅ **Pydantic v2** for data validation
-   🧪 **Comprehensive testing** with pytest
-   🔍 **Code quality tools** (Ruff, Black, MyPy, pre-commit)
-   ⚡ **CI/CD pipeline** with GitHub Actions
-   📝 **Type hints** and static type checking

## Quick Start

### Prerequisites

-   **Python 3.11+**
-   **Poetry** (for dependency management)
-   **Docker and Docker Compose** (for PostgreSQL)

### Installation

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd auth-microservice
    ```

2. **Setup development environment:**

    ```bash
    make setup-dev
    ```

    This will:

    - Install all dependencies
    - Setup pre-commit hooks
    - Configure the development environment

3. **Start PostgreSQL database:**

    ```bash
    docker compose -f docker-compose.db-only.yml up -d
    ```

4. **Run database migrations:**

    ```bash
    make migrate
    ```

5. **Start the development server:**
    ```bash
    make dev
    ```

The API will be available at:

-   **API**: http://localhost:8000
-   **Interactive Docs**: http://localhost:8000/docs
-   **ReDoc**: http://localhost:8000/redoc

## Development Commands

### Environment Setup

```bash
make install       # Install dependencies
make setup-dev     # Setup development environment with pre-commit hooks
```

### Running the Application

```bash
make run          # Run the application (production mode)
make dev          # Run with auto-reload (development mode)
```

### Code Quality

```bash
make lint         # Run linting with Ruff
make lint-fix     # Run linting with auto-fix
make format       # Format code with Black, isort, and Ruff
make type-check   # Run type checking with MyPy
make pre-commit   # Run all pre-commit hooks
make check-all    # Run lint + type-check + tests
```

### Testing

```bash
make test         # Run tests with pytest
make test-cov     # Run tests with coverage report
```

### Database Management

```bash
make migrate                           # Apply database migrations
make upgrade                          # Upgrade to latest migration
make downgrade                        # Downgrade by one migration
make migration msg="description"      # Create new migration
```

### Utilities

```bash
make clean        # Clean cache files and build artifacts
make help         # Show all available commands
```

## API Endpoints

### Authentication

-   `POST /api/v1/auth/signup` - Register new user
-   `POST /api/v1/auth/login` - User login
-   `GET /api/v1/auth/me` - Get current user info
-   `POST /api/v1/auth/refresh` - Refresh access token
-   `POST /api/v1/auth/logout` - Logout user

### Admin (Requires Admin Role)

-   `GET /api/v1/admin/dashboard` - Get admin dashboard with statistics
-   `GET /api/v1/admin/users` - List all users

## Role-Based Authorization

The system supports two roles:

### User Role (`user`)

-   Default role for new registrations
-   Access to basic authentication endpoints
-   Cannot access admin endpoints

### Admin Role (`admin`)

-   Can be assigned during registration or by existing admins
-   Access to all user endpoints
-   Access to admin dashboard and user management

### Example Usage

**Register as admin:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_password",
    "role": "admin"
  }'
```

**Access admin dashboard:**

```bash
curl -X GET "http://localhost:8000/api/v1/admin/dashboard" \
  -H "Authorization: Bearer <admin_access_token>"
```

## Configuration

Environment variables (create `.env` file):

```env
# Application
APP_NAME=Auth Microservice
DEBUG=false
VERSION=1.0.0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://postgres:123456@localhost:5432/authdb

# CORS
ALLOWED_HOSTS=*
```

## Development Tools

### Code Quality Stack

-   **[Ruff](https://docs.astral.sh/ruff/)** - Ultra-fast Python linter and formatter
-   **[Black](https://black.readthedocs.io/)** - Code formatter
-   **[isort](https://pycqa.github.io/isort/)** - Import sorter
-   **[MyPy](https://mypy.readthedocs.io/)** - Static type checker
-   **[pre-commit](https://pre-commit.com/)** - Git hooks framework

### Pre-commit Hooks

Automatically run on every commit:

-   Code formatting (Black, Ruff)
-   Linting (Ruff)
-   Type checking (MyPy)
-   Import sorting (isort)
-   Basic file checks (trailing whitespace, file endings, etc.)
-   Test execution

## Testing

Run the comprehensive test suite:

```bash
make test      # Testes de unidade, integração, e2e
make test-cov  # Testes de cobertura
```

Test categories:

-   **Unit tests** - Individual function testing
-   **Integration tests** - API endpoint testing
-   **Authentication tests** - JWT and password testing
-   **Role-based authorization tests** - Admin access control
-   **Database tests** - Model and migration testing

### Testing Framework

-   **[pytest](https://docs.pytest.org/)** - Testing framework
-   **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)** - Async test support
-   **[pytest-cov](https://pytest-cov.readthedocs.io/)** - Coverage reporting
-   **[httpx](https://www.python-httpx.org/)** - HTTP client for testing

### CI/CD Pipeline

GitHub Actions workflow includes:

-   **Multi-version testing** (Python 3.11, 3.12)
-   **PostgreSQL service** for integration tests
-   **Code quality checks** (linting, type checking)
-   **Security scanning** with Bandit
-   **Coverage reporting** to Codecov
-   **Docker image building** and publishing

## Database Schema

### Users Table

-   `id` - Primary key
-   `username` - Unique username
-   `email` - Unique email address
-   `full_name` - Optional full name
-   `password_hash` - Bcrypt hashed password
-   `role` - User role (admin/user)
-   `created_at` - Timestamp
-   `is_active` - Active status

### Refresh Tokens Table

-   `id` - Primary key
-   `token` - Unique refresh token
-   `user_id` - Foreign key to users
-   `expires_at` - Token expiration
-   `created_at` - Timestamp
-   `is_active` - Active status

## Production Deployment

### Docker

Build and run with Docker:

```bash
docker build -t auth-microservice .
docker run -p 8000:8000 auth-microservice
```

### Environment Variables

For production, ensure these environment variables are set:

-   `SECRET_KEY` - Cryptographically secure secret
-   `DATABASE_URL` - Production database connection
-   `DEBUG=false` - Disable debug mode
-   `ALLOWED_HOSTS` - Restrict CORS origins

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Install development dependencies**: `make setup-dev`
4. **Make your changes**
5. **Run tests and checks**: `make check-all`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines

-   Follow PEP 8 and use the provided code formatting tools
-   Write tests for new features and bug fixes
-   Update documentation for API changes
-   Ensure all CI checks pass
-   Use conventional commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

-   📖 **Documentation**: Check the `/docs` endpoint when running the server
-   🐛 **Issues**: [GitHub Issues](https://github.com/your-username/auth-microservice/issues)
-   💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/auth-microservice/discussions)

---

Built with ❤️ using FastAPI, SQLAlchemy, and modern Python development tools.

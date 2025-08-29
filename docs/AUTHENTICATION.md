# Authentication System Documentation

This authentication system provides secure password hashing with bcrypt and JWT token management with HS256 algorithm.

## 🔧 Features

-   **Password Hashing**: Secure bcrypt hashing with automatic salt generation
-   **JWT Tokens**: HS256 signed tokens with 1-hour expiration
-   **Token Verification**: Automatic token validation with proper error handling
-   **FastAPI Integration**: Ready-to-use dependencies for protected routes

## 📋 Core Functions

### Password Management

#### `get_password_hash(password: str) -> str`

Hash a plain text password using bcrypt.

```python
from src.infrastructure.security.password_service import get_password_hash

# Hash password for storage
hashed = get_password_hash("my_secure_password")
print(hashed)  # $2b$12$randomsaltandhash...
```

#### `verify_password(plain_password: str, hashed_password: str) -> bool`

Verify a plain text password against its bcrypt hash.

```python
from src.infrastructure.security.password_service import verify_password

# Verify password during login
is_valid = verify_password("my_secure_password", hashed_password)
if is_valid:
    print("Password correct!")
else:
    print("Invalid password!")
```

### JWT Token Management

#### `create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str`

Create a JWT access token with HS256 algorithm.

```python
from src.infrastructure.security.token_service import create_access_token
from datetime import timedelta

# Create token with default 1-hour expiration
token_data = {
    "sub": "username",
    "email": "user@example.com",
    "role": "admin"
}
token = create_access_token(token_data)

# Create token with custom expiration
custom_token = create_access_token(
    token_data,
    expires_delta=timedelta(minutes=30)
)
```

#### `decode_token(token: str) -> Dict[str, Any]`

Decode and verify a JWT token.

```python
from src.infrastructure.security.token_service import decode_token

try:
    payload = decode_token(token)
    username = payload.get("sub")
    email = payload.get("email")
    print(f"Authenticated user: {username}")
except HTTPException as e:
    print(f"Token invalid: {e.detail}")
```

### FastAPI Dependencies

#### `get_current_user`

FastAPI dependency to get the current authenticated user from the `Authorization` header.

```python
from fastapi import Depends
from src.api.dependencies import get_current_user
from src.domain.entities.user import User

@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

#### `require_role`

FastAPI dependency to require a specific role for an endpoint.

```python
from fastapi import Depends
from src.api.dependencies import require_role
from src.domain.entities.user import User
from src.infrastructure.database.models.roles import UserRole

@app.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(require_role(UserRole.ADMIN))):
    return {"message": f"Welcome, admin {current_user.username}!"}
```

## 🚀 FastAPI Integration Examples

### Registration Endpoint

```python
from src.api.schemas.user import UserCreate
from src.domain.use_cases.auth_service import AuthService

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
```

### Login Endpoint

```python
from src.api.schemas.user import UserLogin
from src.domain.use_cases.auth_service import AuthService

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
```

### Protected Routes

```python
from src.api.dependencies import get_current_user
from src.domain.entities.user import User

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## 🔐 Security Configuration

### Environment Variables

Make sure to set these in your `.env` file:

```bash
# Strong secret key for JWT signing (change in production!)
SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters

# JWT algorithm
ALGORITHM=HS256

# Token expiration in minutes (60 = 1 hour)
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Production Security Notes

1. **SECRET_KEY**: Use a cryptographically secure random string (at least 32 characters)
2. **HTTPS**: Always use HTTPS in production to protect tokens in transit
3. **Token Storage**: Store tokens securely on the client side (avoid localStorage for sensitive apps)
4. **Rotation**: Implement token refresh if needed for long-lived sessions
5. **Validation**: Always validate tokens on protected endpoints

## 🧪 Testing

Run the authentication test suite using the provided script:

```bash
./run_tests.sh
```

To run tests with coverage:

```bash
./run_tests.sh --coverage
```

## 📡 API Usage Examples

### Register a new user

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d {
       "username": "john_doe",
       "email": "john@example.com",
       "password": "secure_password123"
     \}
```

### Login and get token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d {
       "username": "john_doe",
       "password": "secure_password123"
     \}
```

### Access protected endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## 🔧 Customization

### Custom Token Expiration

```python
# Create token with custom expiration
from datetime import timedelta

# 30-minute token
short_token = create_access_token(
    data={"sub": "username"},
    expires_delta=timedelta(minutes=30)
)

# 24-hour token
long_token = create_access_token(
    data={"sub": "username"},
    expires_delta=timedelta(hours=24)
)
```

### Additional Claims

```python
# Add custom claims to token
token_data = {
    "sub": "username",
    "email": "user@example.com",
    "role": "admin",
    "permissions": ["read", "write", "delete"],
    "organization_id": "org_123"
}
token = create_access_token(token_data)

# Access claims after decoding
payload = decode_token(token)
permissions = payload.get("permissions", [])
org_id = payload.get("organization_id")
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Token has expired"**: The token is older than 1 hour. User needs to login again.
2. **"Could not validate credentials"**: Invalid token format or signature mismatch.
3. **"SECRET_KEY required"**: Make sure SECRET_KEY is set in your environment variables.
4. **Bcrypt version warning**: Harmless warning, functionality works correctly.

### Debug Mode

Enable debug mode to see detailed error messages:

```python
# In config.py
DEBUG: bool = True
```

This will provide more detailed error information during development.

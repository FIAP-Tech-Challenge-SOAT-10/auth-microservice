from datetime import datetime
from pydantic import BaseModel

class RefreshToken(BaseModel):
    id: int
    jti: str
    user_id: int
    token_hash: str
    expires_at: datetime
    created_at: datetime
    is_active: bool
    revoked_at: datetime | None = None

    class Config:
        orm_mode = True

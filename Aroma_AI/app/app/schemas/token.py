from pydantic import BaseModel
from typing import Optional

class TokenPayload(BaseModel):
    sub: Optional[str] = None   # usually user_id ya access_token
    exp: Optional[int] = None   # expiry time (epoch)

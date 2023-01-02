

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    first_name: str = None
    last_name: str = None


class UserToken(Token):
    user_key: str
    user_login_id: str = None
    tenant_id: str = None


class TokenData(BaseModel):
    username: Optional[str] = None

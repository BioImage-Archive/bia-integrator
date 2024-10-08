from pydantic import BaseModel
from typing import Literal, Optional
from uuid import UUID


class BIABaseModel(BaseModel):
    pass


class AuthenticationToken(BIABaseModel):
    access_token: str
    token_type: str


class TokenData(BIABaseModel):
    email: Optional[str] = None


class AuthResult(BIABaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class Pagination(BIABaseModel):
    start_uuid: Optional[UUID] = None
    size: int

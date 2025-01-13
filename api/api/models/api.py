from pydantic import BaseModel, Field
from typing import Literal, Optional
from uuid import UUID
from typing import Dict


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
    start_from_uuid: Optional[UUID] = None
    page_size: int = Field(ge=1)


class DatasetStats(BIABaseModel):
    image_count: int
    file_reference_count: int
    file_reference_size_bytes: int
    file_type_counts: Dict[str, int]

from .persistence import ModelMetadata

from pydantic import BaseModel, validator, ConfigDict
from typing import List, Optional, Dict, Union, Literal
from uuid import UUID
from functools import cached_property

class BIABaseModel(BaseModel):
    pass

class BulkOperationItem(BIABaseModel):
    status: int
    idx_in_request: int
    message: Optional[str]

class BulkOperationResponse(BIABaseModel):
    items: List[BulkOperationItem]
    item_idx_by_status: Dict[int, List[int]] = {}

    """
    Workaround for computed_field not working in fastapi
        * if on 0.101.0 computed_field works as expected but splits input/output models
        * if on later minor version, properties decorated with computed_field are missing from openapi spec 
    """
    def build_item_idx_by_status(self):
        self.item_idx_by_status = {}
        for idx, item in enumerate(self.items):
            self.item_idx_by_status[item.status] = self.item_idx_by_status.get(item.status, [])
            self.item_idx_by_status[item.status].append(idx)

class ObjectInfo(BIABaseModel):
    uuid: UUID
    model: ModelMetadata

class AuthenticationToken(BIABaseModel):
    access_token: str
    token_type: str

class TokenData(BIABaseModel):
    email: Union[str, None] = None

class AuthResult(BIABaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
from .persistence import ModelMetadata

from pydantic import BaseModel, computed_field
from typing import List, Optional, Dict, Union, Literal
from uuid import UUID

class BIABaseModel(BaseModel):
    pass

class BulkOperationItem(BIABaseModel):
    status: int
    idx_in_request: int
    message: Optional[str]

class BulkOperationResponse(BIABaseModel):
    items: List[BulkOperationItem]
    
    @computed_field
    @property
    def item_idx_by_status(self) -> Dict[int, List[int]]:
        """Utility for clients to easily assess if they should retry/correct some items"""
        by_status = {}
        for idx, item in enumerate(self.items):
            by_status[item.status] = by_status.get(item.status, [])
            by_status[item.status].append(idx)
        
        return by_status

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
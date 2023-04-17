from pydantic import BaseModel
from typing import List, Optional, Dict

class BIABaseModel(BaseModel):
    pass

class BulkOperationItem(BIABaseModel):
    status: int
    idx_in_request: int
    message: Optional[str]

class BulkOperationResponse(BIABaseModel):
    items: List[BulkOperationItem]

    @property
    def items_by_status(self) -> Dict[int, BulkOperationItem]:
        """Utility for clients to easily assess if they should retry/correct some items"""
        by_status = {}
        for item in self.items:
            by_status[item.status] = by_status.get(item.status, [])
            by_status[item.status].append(item)

        return by_status
    
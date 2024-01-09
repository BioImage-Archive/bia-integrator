from .persistence import ModelMetadata

from pydantic import BaseModel, Field
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
    item_idx_by_status: Dict[int, List[int]] = {}

    """
    Workaround for computed_field not working in fastapi
        * if on 0.101.0 computed_field works as expected but splits input/output models
        * if on later minor version, properties decorated with computed_field are missing from openapi spec 
    """

    def build_item_idx_by_status(self):
        self.item_idx_by_status = {}
        for idx, item in enumerate(self.items):
            self.item_idx_by_status[item.status] = self.item_idx_by_status.get(
                item.status, []
            )
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


# @TODO: Make Partial[db_models.Annotation] when pydantinc adds partial types
#   see https://github.com/pydantic/pydantic/issues/1673
class SearchAnnotation(BIABaseModel):
    author_email: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    state: Optional[str] = None


class SearchFileRepresentation(BIABaseModel):
    size_bounds_lte: Optional[int] = None
    size_bounds_gte: Optional[int] = None
    type: Optional[str] = None
    # @TODO: Simplify this. Too much variability, https://www.google.com or google.com or www.google.com or https://google.com for the same thing
    #   all might be present even though just two are actual urls
    uri_prefix: Optional[str] = None


class SearchFileReference(BIABaseModel):
    uri_prefix: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    size_bounds_lte: Optional[int] = None
    size_bounds_gte: Optional[int] = None


class SearchStudy(BIABaseModel):
    author_name_fragment: Optional[str] = None
    accession_id: Optional[str] = None
    file_references_count_lte: Optional[int] = None
    file_references_count_gte: Optional[int] = None
    images_count_lte: Optional[int] = None
    images_count_gte: Optional[int] = None
    tag: Optional[str] = None


class SearchStudyFilter(BIABaseModel):
    annotations_any: List[SearchAnnotation] = []
    study_match: Optional[SearchStudy] = None
    start_uuid: Optional[UUID] = None
    limit: int = Field(10, ge=0)


class SearchFileReferenceFilter(BIABaseModel):
    annotations_any: List[SearchAnnotation] = []
    file_reference_match: Optional[SearchFileReference] = None
    study_uuid: Optional[UUID] = None
    start_uuid: Optional[UUID] = None
    limit: int = Field(10, ge=0)


class SearchImageFilter(BIABaseModel):
    original_relpath: Optional[str] = None
    annotations_any: List[SearchAnnotation] = []
    image_representations_any: List[SearchFileRepresentation] = []
    study_uuid: Optional[UUID] = None
    start_uuid: Optional[UUID] = None
    limit: int = Field(10, ge=0)

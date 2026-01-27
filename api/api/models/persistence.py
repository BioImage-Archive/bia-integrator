from typing import List
from uuid import UUID
from bia_shared_datamodels.bia_data_model import DocumentMixin
from pydantic import Field, ConfigDict


class User(DocumentMixin):
    email: str = Field()
    password: str = Field()

    model_config = ConfigDict(model_version_latest=1)

class Embedding(DocumentMixin):
    vector: List[float]
    for_document_uuid: UUID
    additional_metadata: dict[str, str]
    embedding_model: str

    model_config = ConfigDict(model_version_latest=1)
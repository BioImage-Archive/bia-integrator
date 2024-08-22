from bia_shared_datamodels.bia_data_model import DocumentMixin
from pydantic import Field, ConfigDict


class User(DocumentMixin):
    email: str = Field()
    password: str = Field()

    model_config = ConfigDict(model_version_latest=1)

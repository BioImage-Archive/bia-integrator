# ? Import shared models base?


class User(BIABaseModel, DocumentMixin):
    email: str = Field()
    password: str = Field()

    model_config = ConfigDict(model_version_latest=1)

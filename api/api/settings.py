from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    mongo_connstring: str
    mongo_timeout_ms: int
    mongo_collection_users: str = "users"
    mongo_collection_biaint: str = "bia_integrator"
    db_name: str
    jwt_secret_key: str
    user_create_secret_token: str
    fastapi_root_path: str = ""

    # Only pushes indices set in the code (generated from the models/explicit)
    #   to make sure one-off manually added indices are not deleted
    # Run db.bia_integrator.dropIndexes() to delete all indices (then restart app for a refresh)
    mongo_index_push: bool = False

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env", extra="ignore"
    )

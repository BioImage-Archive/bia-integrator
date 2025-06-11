from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    mongo_connstring: str
    mongo_timeout_ms: int
    mongo_max_pool_size: int = Field(
        default=10,
        description="Max size of the Mongo connection pool. The pool is shared among all workers, but we usually run uvicorn with --workers=1",
    )
    mongo_collection_users: str = "users"
    mongo_collection_biaint: str = "bia_integrator"
    db_name: str
    jwt_secret_key: str
    jwt_ttl_minutes: int = 1440
    user_create_secret_token: str
    fastapi_root_path: str = ""

    # Only pushes indices set in the code (generated from the models/explicit)
    #   to make sure one-off manually added indices are not deleted
    # Run db.bia_integrator.dropIndexes() to delete all indices (then restart app for a refresh)
    mongo_index_push: bool = False

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env", extra="ignore"
    )

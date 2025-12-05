from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = Path(__file__).parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="allow")

    cache_root_dirpath: Path = Path.home() / ".cache" / "bia-converter"

    endpoint_url: str = "https://uk1s3.embassy.ebi.ac.uk"
    bucket_name: str = "bia-integrator-data"
    aws_request_checksum_calculation: str = "WHEN_REQUIRED"
    aws_response_checksum_validation: str = "WHEN_REQUIRED"

    bioformats2raw_java_home: str = ""
    bioformats2raw_bin: str = ""
    bioformats2raw_docker_tag: str = "0.9.1"


settings = Settings()

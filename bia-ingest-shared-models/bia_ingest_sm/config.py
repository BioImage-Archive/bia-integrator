from pathlib import Path
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

default_output_base = (
    f"{Path(os.environ.get('HOME', '')) / '.cache' / 'bia-integrator-data-sm'}"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).parent.parent / '.env'}",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # extra="forbid",
    )

    bia_data_dir: str = Field(default_output_base)


#    bioformats2raw_java_home: str = Field()
#    bioformats2raw_bin: str = Field()


# class Settings:
#    def __init__(self):
#        self.bia_data_dir = default_output_base


settings = Settings()

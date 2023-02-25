import os
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    data_dirpath: Path = Path.home()/".bia-integrator-data"

    @property
    def studies_dirpath(self):
        return self.data_dirpath/"studies"

    @property
    def annotations_dirpath(self):
        return self.data_dirpath/"annotations"

    @property
    def images_dirpath(self):
        return self.data_dirpath/"images"

    @property
    def representations_dirpath(self):
        return self.data_dirpath/"representations"

    @property
    def collections_dirpath(self):
        return self.data_dirpath/"collections"


settings = Settings()
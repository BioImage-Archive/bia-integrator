import os
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    data_dirpath: Path = Path.home()/".data"

    @property
    def studies_dirpath(self):
        return self.data_dirpath/"studies"

    @property
    def annotations_dirpath(self):
        return self.data_dirpath/"annotations"
import logging

from pathlib import Path
from typing import Any, Dict, List


logger = logging.getLogger("__main__." + __name__)


def generate_relative_filelist_path(dataset_path: str) -> str:
    return str(Path(dataset_path) / f"file_list.tsv")

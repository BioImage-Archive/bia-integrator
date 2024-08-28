from glob import glob
from pydantic import BaseModel


import json
from pathlib import Path
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def read_api_json_file(file_path: Path, object_type: Type[BaseModel]) -> BaseModel:
    """
    Returns model of object from file to be equivalent to using BIA API Client
    """
    with open(file_path, "r") as object_file:
        object_dict = json.load(object_file)

    return object_type(**object_dict)


def read_all_json(
    directory_path: Path, object_type: Type[BaseModel]
) -> List[BaseModel]:
    object_list = []
    file_paths = sorted(glob(str(directory_path)))
    for file_path in file_paths:
        object_list.append(read_api_json_file(file_path, object_type))
    return object_list

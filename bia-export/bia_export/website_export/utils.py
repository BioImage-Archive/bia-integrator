from glob import glob
from pydantic import BaseModel
from pydantic.alias_generators import to_snake

from .website_models import CLIContext
import json
from pathlib import Path
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def get_source_directory(
    object_type: Type[BaseModel], context: CLIContext
) -> List[Path]:
    file_location = context.root_directory.joinpath(
        f"{to_snake(object_type.__name__)}/{context.accession_id}/*.json"
    )
    return file_location


def read_api_json_file(file_path: Path, object_type: Type[BaseModel]) -> BaseModel:
    """
    Returns model of object from file to be equivalent to using BIA API Client
    """
    with open(file_path, "r") as object_file:
        object_dict = json.load(object_file)

    return object_type(**object_dict)


def read_file_by_uuid_and_type(
    uuid: str, object_type: Type[BaseModel], context: CLIContext
) -> BaseModel:
    file_path = context.root_directory.joinpath(
        f"{to_snake(object_type.__name__)}/{context.accession_id}/{uuid}.json"
    )
    return read_api_json_file(file_path, object_type)


def read_all_json(
    object_type: Type[BaseModel],
    directory_path: Path = None,
    context: CLIContext = None,
) -> List[BaseModel]:
    if not directory_path:
        if not context:
            raise Exception(
                "Need to provide at least one of directory_path or context."
            )
        directory_path = get_source_directory(object_type, context)

    object_list = []
    file_paths = sorted(glob(str(directory_path)))
    for file_path in file_paths:
        object_list.append(read_api_json_file(file_path, object_type))
    return object_list

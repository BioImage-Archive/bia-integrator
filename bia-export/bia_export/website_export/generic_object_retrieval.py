from glob import glob
from uuid import UUID
from pydantic import BaseModel
from pydantic.alias_generators import to_snake
from bia_shared_datamodels.bia_data_model import DocumentMixin
from bia_export.bia_client import api_client
from .website_models import CLIContext
import json
from pathlib import Path
from typing import List, Type
import logging
import threading
import time


logger = logging.getLogger("__main__." + __name__)


class RateLimiter:
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.lock = threading.Lock()
        self.timestamps = []

    def acquire(self):
        while True:
            with self.lock:
                now = time.monotonic()
                cutoff = now - self.period
                self.timestamps = [t for t in self.timestamps if t > cutoff]

                if len(self.timestamps) < self.calls:
                    self.timestamps.append(now)
                    return

                sleep_for = self.timestamps[0] + self.period - now

            if sleep_for > 0:
                time.sleep(sleep_for)


api_rate_limiter = RateLimiter(calls=20, period=5.0)


def get_source_directory(
    object_type: Type[BaseModel], context: CLIContext
) -> List[Path]:
    file_location = context.root_directory.joinpath(
        to_snake(object_type.__name__), context.accession_id, "*.json"
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
        to_snake(object_type.__name__), context.accession_id, f"{uuid}.json"
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


def retrieve_object_list(
    uuid_list: list[UUID], api_class: Type[BaseModel], context: CLIContext
) -> List[BaseModel]:
    if context.root_directory:
        obj_list = []
        for uuid in uuid_list:
            obj_list.append(read_file_by_uuid_and_type(uuid, api_class, context))
    else:
        obj_list = []
        client_method = "get_" + to_snake(api_class.__name__)
        client_function = api_client.__getattribute__(client_method)
        for uuid in uuid_list:
            obj_list.append(client_function(str(uuid)))

    return obj_list


def retrieve_object(
    uuid: list[UUID], api_class: Type[BaseModel], context: CLIContext
) -> List[BaseModel]:
    if context.root_directory:
        obj = read_file_by_uuid_and_type(str(uuid), api_class, context)
    else:
        client_method = "get_" + to_snake(api_class.__name__)
        client_function = api_client.__getattribute__(client_method)
        obj = client_function(str(uuid))

    return obj


def get_all_api_results(
    uuid: UUID,
    api_method,
    page_size_setting=20,
    aggregator_list: list[DocumentMixin] = None,
) -> list[DocumentMixin]:
    api_rate_limiter.acquire()
    if not aggregator_list:
        aggregator_list: list[DocumentMixin] = []
        start_uuid = None
    else:
        start_uuid = aggregator_list[-1].uuid

    fetched_objects = api_method(
        str(uuid),
        page_size=page_size_setting,
        start_from_uuid=str(start_uuid) if start_uuid else None,
    )
    aggregator_list += fetched_objects

    if len(fetched_objects) != page_size_setting:
        return aggregator_list
    else:
        return get_all_api_results(uuid, api_method, page_size_setting, aggregator_list)


def get_one_api_result(uuid: UUID | str, api_method):
    api_rate_limiter.acquire()
    return api_method(uuid)

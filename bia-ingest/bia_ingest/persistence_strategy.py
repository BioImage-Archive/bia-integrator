from uuid import UUID
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Type
from pathlib import Path
import logging

from pydantic import BaseModel
from pydantic.alias_generators import to_snake
from bia_integrator_api.api.private_api import PrivateApi
from bia_integrator_api.api.public_api import PublicApi
from bia_integrator_api.exceptions import NotFoundException
import bia_integrator_api.models as api_models
from bia_ingest.api_client import get_bia_api_client, get_local_bia_api_client
from bia_ingest.settings import get_settings

logger = logging.getLogger("__main__." + __name__)


class PersistenceMode(str, Enum):
    """Destinations for persistence"""

    api = "api"
    local_api = "local_api"
    disk = "disk"


class PersistenceStrategy(ABC):
    @abstractmethod
    def persist(self, object_list: List[BaseModel]) -> None:
        pass

    @abstractmethod
    def fetch_by_uuid(
        self, uuids: List[UUID], model_class: Type[BaseModel]
    ) -> List[BaseModel]:
        """Retrieve specified bia_data_models by their UUIDs"""


# Implement concrete strategies


# Persist to disk
class DiskPersister(PersistenceStrategy):
    def __init__(self, output_dir_base: str, accession_id: str):
        assert (
            len(accession_id) > 0
        ), f"DiskPersister needs to be initialised with an accession id. Got accession_id={accession_id}."
        assert (
            len(output_dir_base) > 0
        ), f"DiskPersister needs to be initialised with a base path for storing artefacts, got: output_dir_base={output_dir_base}"
        self.accession_id = accession_id
        self.output_dir_base = Path(output_dir_base)

    def persist(self, object_list: List[BaseModel]) -> None:
        for obj in object_list:
            object_path = f"{to_snake(obj.model.type_name)}"
            # This is computed in each iteration in case the object list
            # has different types of objects (which we don't expect but is
            # not forbidden)
            output_dir = self.output_dir_base / object_path / self.accession_id
            if not output_dir.is_dir():
                output_dir.mkdir(parents=True)
                logger.debug(f"Created {output_dir}")
            output_path = output_dir / f"{obj.uuid}.json"
            output_path.write_text(obj.model_dump_json(indent=2))
            logger.debug(f"Written {output_path}")

    def fetch_by_uuid(
        self, uuids: List[UUID], model_class: Type[BaseModel]
    ) -> List[BaseModel]:
        model_subdir = f"{to_snake(model_class.__name__)}"
        object_list = []
        for uuid in uuids:
            input_path = (
                self.output_dir_base / model_subdir / self.accession_id / f"{uuid}.json"
            )
            if not input_path.is_file():
                raise NotFoundException
            object_list.append(model_class.model_validate_json(input_path.read_text()))
        return object_list


# Persist using API
class ApiPersister(PersistenceStrategy):
    def __init__(self, api_client: PrivateApi) -> None:
        assert isinstance(api_client, PrivateApi) or isinstance(
            api_client, PublicApi
        ), f"ApiPersister cannot be created. Expected valid instance of <class 'PrivateApi'> or <class 'PublicApi'>. Got : {type(api_client)} - are your API credentials valid and/or is the API server online?"
        self.api_client = api_client

    def persist(self, object_list: List[BaseModel]) -> None:
        for obj in object_list:
            # First try to retrieve object
            try:
                api_copy_of_obj = self.fetch_by_uuid(
                    [
                        f"{obj.uuid}",
                    ],
                    type(obj),
                )[0]
            except NotFoundException:
                api_copy_of_obj = None

            if obj == api_copy_of_obj:
                message = f"Not writing object with uuid: {obj.uuid} and type: {obj.model.type_name} to API because an identical copy of object exists in API"
                logger.warning(message)
                continue
            elif api_copy_of_obj:
                obj.version = api_copy_of_obj.version + 1

            api_obj = getattr(api_models, obj.model.type_name).model_validate_json(
                obj.model_dump_json()
            )

            api_creation_method = f"post_{to_snake(obj.model.type_name)}"
            getattr(self.api_client, api_creation_method)(api_obj)
            logger.debug(f"persisted {obj.uuid} of type {obj.model.type_name} to API")

    def fetch_by_uuid(
        self, uuids: List[UUID | str], model_class: Type[BaseModel]
    ) -> List[BaseModel]:
        object_list = []
        for uuid in uuids:
            api_get_method = f"get_{to_snake(model_class.__name__)}"
            api_obj = getattr(self.api_client, api_get_method)(str(uuid))
            obj = model_class.model_validate_json(api_obj.model_dump_json())
            object_list.append(obj)
        return object_list


# Replacement for persist function using a persistence strategy
def persist(object_list: List[BaseModel], strategy: PersistenceStrategy) -> None:
    strategy.persist(object_list)


def persistence_strategy_factory(persistence_mode: PersistenceMode, **kwargs):
    # Raise error if user passes in a value that cannot be converted
    # to a valid persistence strategy
    persistence_mode = PersistenceMode(persistence_mode)

    if persistence_mode == PersistenceMode.api:
        return ApiPersister(api_client=get_bia_api_client())
    elif persistence_mode == PersistenceMode.local_api:
        return ApiPersister(api_client=get_local_bia_api_client())
    elif persistence_mode == PersistenceMode.disk:
        return DiskPersister(
            output_dir_base=get_settings().bia_data_dir,
            accession_id=kwargs["accession_id"],
        )
    else:
        raise Exception(f"Unknown persistence strategy: {persistence_mode}")

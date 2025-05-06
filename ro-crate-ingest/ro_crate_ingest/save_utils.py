from .settings import get_settings
from pathlib import Path
import os
from bia_shared_datamodels import bia_data_model
from typing import Type
from enum import Enum
from pydantic.alias_generators import to_snake
from enum import Enum
from .api_client import get_local_bia_api_client, get_bia_api_client
import bia_integrator_api.models as api_models
from bia_integrator_api.exceptions import NotFoundException
import logging

logger = logging.getLogger("__main__." + __name__)


class PersistenceMode(str, Enum):
    """
    Enum for the different persistance modes.
    """

    LOCAL_FILE = "local_file"
    LOCAL_API = "local_api"
    BIA_API = "bia_api"


def save_local_individual_file(object_dir: Path, object_to_save):

    object_to_save = round_trip_object_class_from_client_to_datamodel(object_to_save)

    with open(object_dir / f"{object_to_save.uuid}.json", "w") as file:
        file.write(object_to_save.model_dump_json(indent=2))


def save_local_file(
    accession_id: str,
    object_type: Type[bia_data_model.DocumentMixin],
    objects_to_save: list[bia_data_model.DocumentMixin],
):

    local_cache_dir = Path(get_settings().bia_data_dir)

    if not os.path.exists(local_cache_dir):
        os.makedirs(get_settings().bia_data_dir)

    object_type_dir = local_cache_dir / to_snake(object_type.__name__)

    if not os.path.exists(object_type_dir):
        os.makedirs(object_type_dir)

    object_dir = object_type_dir / accession_id

    if not os.path.exists(object_dir):
        os.makedirs(object_dir)

    for document in objects_to_save:
        save_local_individual_file(object_dir, document)


def fetch_document(
    object_type: Type[bia_data_model.DocumentMixin],
    document: bia_data_model.DocumentMixin,
    api_client,
):
    try:
        api_get_method = f"get_{to_snake(object_type.__name__)}"
        api_obj = getattr(api_client, api_get_method)(str(document.uuid))
    except NotFoundException:
        api_obj = None

    return api_obj


def save_local_api(
    object_type: Type[bia_data_model.DocumentMixin],
    objects_to_save: list[bia_data_model.DocumentMixin],
):
    client = get_local_bia_api_client()
    save_api(client, object_type, objects_to_save)


def save_bia_api(
    object_type: Type[bia_data_model.DocumentMixin],
    objects_to_save: list[bia_data_model.DocumentMixin],
):
    client = get_bia_api_client()
    save_api(client, object_type, objects_to_save)


def save_api(
    client,
    object_type: Type[bia_data_model.DocumentMixin],
    objects_to_save: list[bia_data_model.DocumentMixin],
):
    for obj in objects_to_save:

        obj = round_trip_object_class_from_client_to_datamodel(obj)

        api_copy_of_obj = fetch_document(object_type, obj, client)
        if api_copy_of_obj:
            if obj == api_copy_of_obj:
                message = f"Not writing object with uuid: {obj.uuid} and type: {obj.model.type_name} to API because an identical copy of object exists in API"
                logger.warning(message)
                continue
            elif api_copy_of_obj:
                obj.version = api_copy_of_obj.version + 1

        api_obj = getattr(api_models, object_type.__name__).model_validate_json(
            obj.model_dump_json()
        )
        api_creation_method = f"post_{to_snake(object_type.__name__)}"
        post_function = getattr(client, api_creation_method)
        post_function(api_obj)


def persist(
    accession_id: str,
    object_type: Type[bia_data_model.DocumentMixin],
    objects_to_save: list[bia_data_model.DocumentMixin],
    persistence_mode: PersistenceMode,
):

    if persistence_mode == PersistenceMode.LOCAL_FILE:
    if persistence_mode == PersistenceMode.LOCAL_FILE:
        save_local_file(accession_id, object_type, objects_to_save)
    elif persistence_mode == PersistenceMode.LOCAL_API:
        save_local_api(object_type, objects_to_save)
    elif persistence_mode == PersistenceMode.BIA_API:
        save_bia_api(object_type, objects_to_save)
    else:
        raise ValueError(
            f"Something went wrong with the persistance mode: {persistence_mode}"
        )


def round_trip_object_class_from_client_to_datamodel(api_object):
    """
    This function is used to add in the information that the API would automatically add to the object.
    This is to deal enable the ingest to check if the object has been changed and only bump the object version if it has.
    Otherwise, the comparison would always fail because the API is adding e.g. model information to the object.
    """
    obj_class_api = api_object.__class__
    bia_data_model_class = getattr(bia_data_model, obj_class_api.__name__)

    obj_bia_data_model = bia_data_model_class.model_validate_json(
        api_object.model_dump_json()
    )

    original_object = obj_class_api.model_validate_json(
        obj_bia_data_model.model_dump_json()
    )

    return original_object

from pathlib import Path
from uuid import UUID
from pydantic import BaseModel, ValidationError
import hashlib
import uuid
from typing import Any, Dict, List, Type

from bia_ingest.cli_logging import IngestionResult, log_failed_model_creation
from bia_ingest.config import settings


def filter_model_dictionary(dictionary: dict, target_model: Type[BaseModel]):
    accepted_fields = target_model.model_fields.keys()
    result_dict = {key: dictionary[key] for key in accepted_fields if key in dictionary}
    return result_dict


def dict_to_uuid(my_dict: Dict[str, Any], attributes_to_consider: List[str]) -> str:
    """
    Create uuid from specific keys in a dictionary
    """
    # TODO: Need to use a canonical version for this function e.g. from API

    seed = "".join([f"{my_dict[attr]}" for attr in attributes_to_consider])
    hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return str(uuid.UUID(version=4, hex=hexdigest))


def dicts_to_api_models(
    dicts: List[Dict[str, Any]],
    api_model_class: Type[BaseModel],
    valdiation_error_tracking: IngestionResult,
) -> BaseModel:
    """
    This function instantiates any API model given a dict of its attributes
    Hence the use of the pydantic BaseModel which all API models are derived from in the type hinting
    """
    api_models = []
    for model_dict in dicts:
        try:
            api_models.append(api_model_class.model_validate(model_dict))
        except ValidationError:
            log_failed_model_creation(api_model_class, valdiation_error_tracking)
    return api_models


def get_bia_data_model_by_uuid(
    uuid: UUID, model_class: Type[BaseModel], accession_id: str = ""
) -> BaseModel:
    """Instantiate a bia_data_model from a json file on disk"""
    # TODO: Find out how to get generic type for bia_data_model (baseclass?)
    import re

    model_name_parts = [
        s.lower() for s in re.split(r"(?=[A-Z])", model_class.__name__) if len(s) > 0
    ]
    model_subdir = "_".join(model_name_parts) + "s"
    input_path = (
        Path(settings.bia_data_dir) / model_subdir / accession_id / f"{uuid}.json"
    )
    return model_class.model_validate_json(input_path.read_text())

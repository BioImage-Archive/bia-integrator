from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Type, Optional

from bia_ingest.cli_logging import (
    IngestionResult,
    log_failed_model_creation,
    log_model_creation_count,
)


def dict_to_api_model(
    dict: dict[str, Any],
    api_model_class: Type[BaseModel],
    valdiation_error_tracking: IngestionResult,
) -> Optional[BaseModel]:
    api_model = None
    try:
        api_model = api_model_class.model_validate(dict)
    except ValidationError:
        log_failed_model_creation(api_model_class, valdiation_error_tracking)
    if api_model:
        log_model_creation_count(api_model_class, 1, valdiation_error_tracking)
    return api_model


def dicts_to_api_models(
    dicts: List[Dict[str, Any]],
    api_model_class: Type[BaseModel],
    valdiation_error_tracking: IngestionResult,
) -> List[BaseModel]:
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

    log_model_creation_count(
        api_model_class, len(api_models), valdiation_error_tracking
    )
    return api_models


def dict_map_to_api_models(
    dicts: dict[str, dict[str, Any]],
    api_model_class: Type[BaseModel],
    valdiation_error_tracking: IngestionResult,
) -> dict[str, BaseModel]:
    """
    This function instantiates any API model given a dict of its attributes
    Hence the use of the pydantic BaseModel which all API models are derived from in the type hinting
    """
    api_models = {}
    for reference_id, model_dict in dicts.items():
        try:
            api_models[reference_id] = api_model_class.model_validate(model_dict)
        except ValidationError:
            log_failed_model_creation(api_model_class, valdiation_error_tracking)

    log_model_creation_count(
        api_model_class, len(api_models), valdiation_error_tracking
    )
    return api_models

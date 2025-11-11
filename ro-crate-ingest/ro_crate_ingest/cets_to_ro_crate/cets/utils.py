import logging

from typing import Any, Type
from pydantic import BaseModel, ValidationError


logger = logging.getLogger(__name__)


def dict_to_cets_model(
    model_data: dict[str, Any], 
    cets_model_class: Type[BaseModel], 
) -> BaseModel:
    
    try:
        return cets_model_class.model_validate(model_data)
    except ValidationError as e:
        logger.error(
            f"Validation error for {cets_model_class.__name__}: {e}"
        )
        raise

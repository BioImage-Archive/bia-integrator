from pydantic import BaseModel
import hashlib
import uuid
from typing import Any, Dict, List, Type


def filter_model_dictionary(dictionary: dict, target_model: Type[BaseModel]):
    accepted_fields = target_model.model_fields.keys()
    result_dict = {key: dictionary[key] for key in accepted_fields if key in dictionary}
    return result_dict

# TODO: Need to use a canonical version for this function e.g. from API
def dict_to_uuid(my_dict: Dict[str, Any], attributes_to_consider: List[str]) -> str:
    """
    Create uuid from specific keys in a dictionary
    """

    seed = "".join([f"{my_dict[attr]}" for attr in attributes_to_consider])
    hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return str(uuid.UUID(version=4, hex=hexdigest))

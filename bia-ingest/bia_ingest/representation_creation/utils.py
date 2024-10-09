from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger("__main__." + __name__)


def get_image_extension(file_path: str) -> str:
    """Return standardized image extension for a given file path."""

    # Process files with multi suffix extensions
    multi_suffix_ext = {
        ".ome.zarr.zip": ".ome.zarr.zip",
        ".zarr.zip": ".zarr.zip",
        ".ome.zarr": ".ome.zarr",
        ".ome.tiff": ".ome.tiff",
        ".ome.tif": ".ome.tiff",
        ".tar.gz": ".tar.gz",
    }

    for ext, mapped_value in multi_suffix_ext.items():
        if file_path.lower().endswith(ext):
            return mapped_value

    # Standardise extensions expressed using different suffixes
    ext_map = {
        ".jpeg": ".jpg",
        ".tif": ".tiff",
    }

    ext = Path(file_path).suffix.lower()
    if ext in ext_map:
        return ext_map[ext]
    else:
        return ext


def merge_dicts(dict_list: List[Dict[str, str]]) -> Dict:
    """Merge list of dicts to one dict. Values for repeated keys are put into lists

    Assumes all input dict values are strings as in function type hint
    """

    if not dict_list:
        return {}

    merged_dict = dict_list[0]

    for dictionary in dict_list[1:]:
        for key, value in dictionary.items():
            # If the key already exists in the merged dictionary
            if key in merged_dict:
                # If it's not already a list, convert the current value to a list
                if not isinstance(merged_dict[key], list):
                    merged_dict[key] = [merged_dict[key]]
                # Append the new value to the list
                merged_dict[key].append(value)
            else:
                # If the key does not exist, add it to the merged dictionary
                merged_dict[key] = value

    return merged_dict

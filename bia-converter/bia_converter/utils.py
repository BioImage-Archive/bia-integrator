import os
import logging
from uuid import UUID
from typing import Union
from pathlib import Path


from bia_integrator_api.models import (  # type: ignore
    ImageRepresentation,
)

from .bia_api_client import api_client


logger = logging.getLogger(__name__)


def create_s3_uri_suffix_for_image_representation(
    representation: ImageRepresentation,
) -> str:
    """Create the part of the s3 uri that goes after the bucket name for an image representation"""

    assert representation.image_format and len(representation.image_format) > 0
    assert isinstance(representation.representation_of_uuid, UUID) or isinstance(
        UUID(representation.representation_of_uuid), UUID
    )
    input_image = api_client.get_image(representation.representation_of_uuid)
    dataset = api_client.get_dataset(input_image.submission_dataset_uuid)
    study = api_client.get_study(dataset.submitted_in_study_uuid)
    return f"{study.accession_id}/{representation.representation_of_uuid}/{representation.uuid}{representation.image_format}"


def attributes_by_name(model_object):
    """
    Converts a list of Attribute objects into a dictionary mapping attribute names to their values.

    Args:
        model_object: An object containing an 'attributes' property that holds a list of Attribute objects.
                    Each Attribute object must have 'name' and 'value' properties.

    Returns:
        dict: A dictionary where the keys are attribute names and values are the corresponding attribute values.
                For example:
                {
                    'imageset_metadata': {'pixel_width': 6.34, 'pixel_height': 6.34, ...},
                    'dirpath_prefix': {'prefix': 'data/E.gracilis/raw/raw'}
                }
    """

    return {attribute.name: attribute.value for attribute in model_object.attribute}


def get_dir_size(path: Union[str, Path]) -> int:
    """
    Calculate total size of a directory tree in bytes.

    Args:
        path: Directory path to analyze

    Returns:
        int: Total size in bytes

    Example:
        >>> size_bytes = get_dir_size("/path/to/dir")
        >>> size_mb = size_bytes / (1024 * 1024)  # Convert to MB
    """
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(f"{path} is not a directory")

    total_size = 0

    # Use os.walk for better performance than Path.rglob
    for dirpath, dirnames, filenames in os.walk(root):
        # Add sizes of all files in current directory
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # Use os.path.getsize and handle file access errors
            try:
                total_size += os.path.getsize(file_path)
            except (OSError, IOError):
                # Skip files we can't access
                continue

    return total_size

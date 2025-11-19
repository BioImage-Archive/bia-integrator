import os
import logging
from uuid import UUID
from typing import Union
from pathlib import Path

import zarr
from pydantic_core._pydantic_core import ValidationError
from .omezarrmeta import ZMeta

from bia_integrator_api.models import (  # type: ignore
    ImageRepresentation,
    Attribute,
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


def image_dimensions_as_string(dims: list[int] | tuple[int, int]) -> str:
    return "_".join([str(d) for d in dims])


def create_s3_uri_suffix_for_2d_view_of_image_representation(
    representation: ImageRepresentation,
    dims: tuple,
    name: str,
    image_format: str = ".png",
) -> str:
    """Create the part of the uri that goes after the bucket name for a 2D view of an image representation"""

    assert isinstance(representation.representation_of_uuid, UUID) or isinstance(
        UUID(representation.representation_of_uuid), UUID
    )
    input_image = api_client.get_image(representation.representation_of_uuid)
    dataset = api_client.get_dataset(input_image.submission_dataset_uuid)
    study = api_client.get_study(dataset.submitted_in_study_uuid)

    dims_as_str = image_dimensions_as_string(dims)

    assert len(image_format) > 0
    if image_format[0] != ".":
        image_format = "." + image_format

    return f"{study.accession_id}/{representation.representation_of_uuid}/{name}_{dims_as_str}{image_format}"


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

    return {
        attribute.name: attribute.value
        for attribute in model_object.additional_metadata
    }


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


def add_or_update_attribute(attribute_to_add: Attribute, attributes: list[Attribute]):
    """
    Idempotently add or update an attribute in attributes.

    Parameters:
    - attributes: list of bia_shared_models.Attribute
    - name: the name of the attribute to add or update
    - value: the value to set for the attribute
    """

    for i, attr in enumerate(attributes):
        if attr.name == attribute_to_add.name:
            # We treat 'static_image_uri' and 'thumbnail_uri' differently
            # The value can have multiple keys. E.g.
            # {
            #   "256": value_for_256,
            #   "512": value_for_512
            # }
            # so we update values instead or replace.
            if attr.name == "image_static_display_uri" or attr.name == "thumbnail_uri":
                attributes[i].value.update(attribute_to_add.value)
            else:
                attributes[i].value = attribute_to_add.value
            return
    # If not found, append it
    attributes.append(attribute_to_add)


def is_zarr_multiscales(zarr_path: Path) -> bool:
    """
    Check if a given Zarr is multiscales

    Parameters:
    - zarr_path: Path to the Zarr directory.

    Returns:
    - bool: True if the Zarr directory is multiscales, False otherwise.
    """
    zattrs_path = zarr_path / ".zattrs"
    if not zattrs_path.is_file():
        return False

    try:
        import json

        with open(zattrs_path, "r") as f:
            zattrs_content = json.load(f)
            return "multiscales" in zattrs_content
    except (json.JSONDecodeError, IOError):
        return False
    return


def determine_ome_zarr_type(zarr_path):
    """
    Determine the type of OME-Zarr format based on the metadata of the given Zarr group.

    Args:
        zarr_path (str): The URL or path to the OME-Zarr file.

    Returns:
            - "hcs": If the Zarr group contains an HCS (High Content Screening) image.
            - "bf2rawtr": If the Zarr group contains a BioFormats2RawTr image.
            - "v04image": If the Zarr group contains an OME v4 image.
            - "v05image": If the Zarr group contains an OME v5 image.
            - "unknown": If the Zarr group does not match any of the known OME-Zarr formats.

    Based on bia_zarr.thing.determine_thing in https://github.com/BioImage-Archive/bia-zarr
    """
    try:
        zarr_group = zarr.open_group(zarr_path, mode="r")
    except (FileNotFoundError, IOError) as e:
        logger.warning(f"Got error {e} attempting to open zarr group")
        return "unknown"

    if zarr_group.metadata.zarr_format == 2:
        if "plate" in zarr_group.attrs:
            return "hcs"
        if dict(zarr_group.attrs) == {"bioformats2raw.layout": 3}:
            return "bf2rawtr"
        else:
            try:
                ZMeta.model_validate(zarr_group.attrs)
                return "v04image"
            except (IOError, ValidationError) as e:
                logger.warning(f"Got errore {e} attempting to validate v04image")
                return "unknown"
    elif zarr_group.metadata.zarr_format == 3:
        try:
            ZMeta.model_validate(zarr_group.attrs["ome"])
            return "v05image"
        except (IOError, ValidationError) as e:
            logger.warning(f"Got errore {e} attempting to validate v04image")
            return "unknown"

    return "Unknown"


def create_vizarr_compatible_ome_zarr_uri(original_zarr_group_uri: str) -> str:
    """
    Customised check for vizarr compatible hcs or image uri. If unknown return original uri.

    """

    ACCEPTED_ZARR_TYPES = [
        "hcs",
        "v04image",
        "v05image",
    ]
    zarr_group_uri = original_zarr_group_uri.strip()

    while zarr_group_uri.endswith("/"):
        zarr_group_uri = zarr_group_uri.rstrip("/")

    ome_zarr_type = determine_ome_zarr_type(zarr_group_uri)
    if ome_zarr_type in ACCEPTED_ZARR_TYPES:
        return zarr_group_uri
    else:
        # Reconstruct uri and try again
        if ome_zarr_type == "bf2rawtr":
            zarr_group_uri = zarr_group_uri + "/0"
        elif zarr_group_uri.endswith("/0"):
            # Strip "/0" and retry
            zarr_group_uri = zarr_group_uri[:-2]
        else:
            # Otherwise append "/0" and retry
            zarr_group_uri = zarr_group_uri + "/0"

        # Try again with reconstructed uri
        ome_zarr_type = determine_ome_zarr_type(zarr_group_uri)
        if ome_zarr_type in ACCEPTED_ZARR_TYPES:
            return zarr_group_uri
        else:
            return original_zarr_group_uri


def find_multiscale_well_uri(zarr_uri):
    """
    Find a well with a multiscale image in it and return the URI to the top level of the well.

    Args:
        zarr_uri (str): The URI to the high content screen Zarr archive.

    Returns:
        str: The URI to the top level of the well containing the multiscale image.

    Raises:
        ValueError: If no well with a multiscale image is found in the Zarr archive.
    """
    # Open the Zarr archive
    zarr_group = zarr.open_group(zarr_uri)

    # Iterate over all the wells in the Zarr archive
    for row in zarr_group.keys():
        for col in zarr_group[row].keys():
            for image in zarr_group[row][col].keys():
                # Check if the well contains a multiscale image
                well_uri = "/".join([zarr_uri, row, col, image])
                ome_zarr_type = determine_ome_zarr_type(well_uri)
                if ome_zarr_type.endswith("image"):
                    return well_uri

    # Raise an error if no well with a multiscale image is found
    raise ValueError(
        f"No well with a multiscale image found in the Zarr archive: {zarr_uri}"
    )


def create_uri_for_extracting_2d_image_from_ome_zarr(uri):
    """Returns URI to a multiscale image. For HCS returns URI to a well with a multiscale image."""

    ome_zarr_uri = create_vizarr_compatible_ome_zarr_uri(uri)
    ome_zarr_type = determine_ome_zarr_type(ome_zarr_uri)
    if ome_zarr_type.endswith("image"):
        return ome_zarr_uri
    elif ome_zarr_type == "hcs":
        return find_multiscale_well_uri(ome_zarr_uri)
    else:
        raise ValueError(f"Could not get URI for multiscale image from: {uri}")

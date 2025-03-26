import os
import logging
from uuid import UUID
from typing import Union, Tuple
from pathlib import Path

from .neuroglancer import Layer, ViewerState, state_to_ng_uri, InvlerpParameters


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


def generate_ng_link_for_zarr(
        ome_zarr_uri: str, 
        contrast_bounds: Tuple[float, float],
        position: Tuple[int, int, int],
        physical_sizes: Tuple[float, float, float] 
) -> str:
    
    """Given the URI to an OME-Zarr file, a label for that image,
    generate a Neuroglancer link at which the image+annotations 
    can be visualised.
    
    """

    lower_bound, upper_bound = contrast_bounds

    shader_controls = {
        "normalized" : InvlerpParameters(
            range = (lower_bound, upper_bound),
            window = None,
            channel = None
        )
    }

    base_layer = Layer(
        type="image",
        source=f"{ome_zarr_uri}/|zarr2:",
        name="image",
        volumeRendering=False,
        shaderControls=shader_controls
    )

    v = ViewerState(
        dimensions={
            "t": (1, ""),
            "c": (1, ""),
            "z": (physical_sizes[0], "m"),
            "y": (physical_sizes[1], "m"),
            "x": (physical_sizes[2], "m"),
        },
        displayDimensions=["x", "y", "z"],
        position=[0, 0, position[0], position[1], position[2]], # position is stil tczyx regardless of displayDimensions
        crossSectionScale=5, #TODO: work out best way to calculate this
        layers=[base_layer],
        layout="4panel"
    )

    state_uri = state_to_ng_uri(v, "https://neuroglancer-demo.appspot.com/#!")

    return state_uri
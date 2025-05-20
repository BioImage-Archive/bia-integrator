import os
import logging
from uuid import UUID
from typing import Union, Tuple
from pathlib import Path
from pandas import DataFrame
import rich
import json

from .neuroglancer import Layer, ViewerState, state_to_ng_uri, InvlerpParameters

from bia_integrator_api.models import (  # type: ignore
    AnnotationData, 
    Attribute, 
    Image, 
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


def filter_starfile_df(
        star_df: DataFrame, 
        annotation: AnnotationData, 
        image_uuid: str, 
) -> DataFrame:
    """Filter a starfile (as a dataframe) for a pattern specified in annoation data, if applicable, 
    and return the X, Y, and Z coordinates of that filtered part."""

    attrs = attributes_by_name(annotation)
    pattern_list = attrs['annotated_image_patterns']['annotated_image_patterns']
    image_pattern = [pattern[image_uuid] for pattern in pattern_list if image_uuid in pattern][0] # assume one pattern per image
    rich.print(f"Image pattern: {image_pattern}")
    if image_pattern is None:
        filtered_df = star_df
    else:
        filtered_df = star_df[star_df["rlnMicrographName"] == image_pattern]

    columns_to_save = ["rlnCoordinateX", "rlnCoordinateY", "rlnCoordinateZ"]
    filtered_df = filtered_df[columns_to_save]

    return filtered_df


def write_starfile_df_to_json(
        star_df: DataFrame, 
        output_json_path: Path, 
) -> str:
    
    star_df_dict = star_df.to_dict(orient='records')
    
    output_json_path.mkdir(exist_ok=True, parents=True)
    output_file = output_json_path / "annotation_data.json"
    with open(output_file, 'w') as f:
        json.dump(star_df_dict, f, indent=2)


def add_json_file_path_to_annotation(
        annotation: AnnotationData, 
        image_uuid: str, 
        json_file_path: str, 
) -> AnnotationData:
    
    new_json_path = {image_uuid: json_file_path}
    
    annotation_file_paths_attr = None
    for attr in annotation.attribute:
        if attr.name == "annotation_file_paths":
            annotation_file_paths_attr = attr
            break
    
    if annotation_file_paths_attr:
        annotation_file_paths_attr.value["annotation_file_paths"].append(new_json_path)
    else:
        file_path_attr = Attribute(
            provenance="bia_conversion",
            name="annotation_file_paths",
            value={
                "annotation_file_paths": [new_json_path]
            }
        )
        annotation.attribute.append(file_path_attr)
    
    return annotation


def add_ng_precomp_file_path_to_annotation(
        annotation: AnnotationData, 
        image_uuid: str, 
        ng_precomp_file_path: str, 
) -> AnnotationData:
    
    new_ng_precomp_path = {image_uuid: ng_precomp_file_path}
    
    annotation_file_paths_attr = None
    for attr in annotation.attribute:
        if attr.name == "ng_precomp_file_paths":
            annotation_file_paths_attr = attr
            break
    
    if annotation_file_paths_attr:
        annotation_file_paths_attr.value["ng_precomp_file_paths"].append(new_ng_precomp_path)
    else:
        file_path_attr = Attribute(
            provenance="bia_conversion",
            name="ng_precomp_file_paths",
            value={
                "ng_precomp_file_paths": [new_ng_precomp_path]
            }
        )
        annotation.attribute.append(file_path_attr)
    
    return annotation


def update_annotated_image_and_image_rep(
        image_uuid: str, 
        image_rep: ImageRepresentation, 
        ng_uri_link: str, 
) -> tuple[Image, ImageRepresentation]:
    
    ng_view_link_attr = None
    for attr in image_rep.attribute:
        if attr.name == "neuroglancer_view_link":
            ng_view_link_attr = attr
            break
    
    if ng_view_link_attr:
        ng_view_link_attr.value["neuroglancer_view_link"] = ng_uri_link
        ng_view_link_attr.provenance = "bia_conversion"
    else:
        ng_view_link_attr = Attribute(
            provenance="bia_conversion",
            name="neuroglancer_view_link",
            value={
                "neuroglancer_view_link": ng_uri_link
            }
        )
        image_rep.attribute.append(ng_view_link_attr)

    image = api_client.get_image(image_uuid)
    pref_ng_link_attr = None
    for attr in image_rep.attribute:
        if attr.name == "preferred_neuroglancer_image_representation_uuid":
            pref_ng_link_attr = attr
            break
    
    if pref_ng_link_attr:
        pref_ng_link_attr.value["preferred_neuroglancer_image_representation_uuid"] = image_rep.uuid
        pref_ng_link_attr.provenance = "bia_conversion"
    else:
        pref_ng_link_attr = Attribute(
            provenance="bia_conversion",
            name="preferred_neuroglancer_image_representation_uuid",
            value={
                "preferred_neuroglancer_image_representation_uuid": image_rep.uuid
            }
        )
        image.attribute.append(pref_ng_link_attr)
    
    return image, image_rep


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


def generate_ng_link_for_zarr_and_precomp_annotation(
        ome_zarr_uri: str, 
        precomp_annotation_uri: str, 
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

    annotations_layer = Layer(
        type="annotation",
        source=f"precomputed://{precomp_annotation_uri}",
        tab="annotations",
        name="particles",
        annotationColor="#FFFF00"
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
        layers=[base_layer, annotations_layer],
        layout="4panel"
    )

    state_uri = state_to_ng_uri(v, "https://neuroglancer-demo.appspot.com/#!")

    return state_uri
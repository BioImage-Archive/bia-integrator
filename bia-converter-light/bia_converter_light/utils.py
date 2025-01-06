from pydantic import BaseModel
from uuid import UUID
from pathlib import Path
from typing import Dict, List
import logging
import xml.etree.ElementTree as ET

from pydantic.alias_generators import to_snake

from bia_integrator_api.exceptions import NotFoundException
import bia_integrator_api.models as api_models
from bia_shared_datamodels import bia_data_model
from bia_converter_light.config import settings, api_client

logger = logging.getLogger("__main__." + __name__)


def get_total_zarr_size(zarr_path: str) -> int:
    """Return size of zarr archive in bytes"""

    # Assume the zarr store is a local disk
    # TODO: Generalise for any uri (including file:// and s3://)
    # TODO: so the argument name for this func should be 'zarr_uri'
    zarr_path = Path(zarr_path)
    return (
        sum(f.stat().st_size for f in zarr_path.rglob("*")) + zarr_path.stat().st_size
    )


single_file_formats_path = (
    Path(__file__).parent / "resources" / "bioformats_curated_single_file_formats.txt"
)
single_file_formats = [
    s for s in single_file_formats_path.read_text().split("\n") if len(s) > 0
]


def extension_in_bioformats_single_file_formats_list(ext: str) -> bool:
    if len(ext) > 1 and not ext[0] == ".":
        ext = "." + ext
    return ext in single_file_formats


def in_bioformats_single_file_formats_list(file_location: [Path | str]) -> bool:
    """Check if ext of path/uri/name of file in bioformats single file formats list"""
    ext = get_image_extension(f"{file_location}")
    return extension_in_bioformats_single_file_formats_list(ext)


def get_ome_zarr_pixel_metadata(zarr_location: str) -> dict:
    """Return pixel metadata entry of METADATA.ome.xml of bioformats2raw zarr"""

    # This function assumes the zarr has been created at specified location
    # on disk and was produced by bioformats2raw -> OME/METADATA.ome.xml
    # exists
    #
    # TODO: handle general uris e.g. https://, s3:// or file://
    metadata_path = Path(zarr_location) / "OME" / "METADATA.ome.xml"
    if metadata_path.is_file():
        metadata = parse_xml_string(metadata_path.read_text())
        try:
            image_metadata = metadata[
                "{http://www.openmicroscopy.org/Schemas/OME/2016-06}OME"
            ][r"{http://www.openmicroscopy.org/Schemas/OME/2016-06}Image"]

            # Multichannel images may have a list - use first element
            # TODO: Discuss with team what to do in this case
            if isinstance(image_metadata, list):
                image_metadata = image_metadata[0]

            pixel_metadata = image_metadata[
                "{http://www.openmicroscopy.org/Schemas/OME/2016-06}Pixels"
            ]
        except KeyError:
            pixel_metadata = {}
    else:
        pixel_metadata = {}

    return pixel_metadata


# TODO: discuss replacing this function with something from either
#       ome_zarr or ome_zarr_metadata
def parse_xml_string(xml_string: str) -> dict:
    """
    Parse an XML string and convert it into a dictionary.

    This is intended to be used for OME/METADATA.ome.xml created
    by bioformats2raw.
    """

    def _xml_to_dict(element: ET) -> dict:
        """
        Convert XML element and children to a dict, including attributes.
        """
        # Initialize the dictionary to store the element's data
        result = {}

        # Include attributes in the result if they exist
        if element.attrib:
            result.update({k: v for k, v in element.attrib.items()})

        # If the element has no children, return its text or result if there are attributes
        if len(element) == 0:
            return element.text if not result else result

        # Iterate over the children of the element
        for child in element:
            child_dict = _xml_to_dict(child)

            # Handle duplicate tags by storing them as a list
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]
            else:
                result[child.tag] = child_dict

        return result

    # Parse the XML string into an ElementTree
    root = ET.fromstring(xml_string)

    # Convert the ElementTree into a dictionary
    return {root.tag: _xml_to_dict(root)}


def create_s3_uri_suffix_for_image_representation(
    accession_id: str, representation: bia_data_model.ImageRepresentation
) -> str:
    """Create the part of the s3 uri that goes after the bucket name for an image representation"""

    assert representation.image_format and len(representation.image_format) > 0
    assert isinstance(representation.representation_of_uuid, UUID) or isinstance(
        UUID(representation.representation_of_uuid), UUID
    )
    return f"{accession_id}/{representation.representation_of_uuid}/{representation.uuid}{representation.image_format}"


def get_local_path_for_representation(uuid: [str | UUID], image_format: str) -> Path:
    """Return path to local cache for this image representation"""

    if not image_format.startswith("."):
        image_format = f".{image_format}"
    cache_dirpath = settings.cache_root_dirpath / "other_converted_images"
    cache_dirpath.mkdir(exist_ok=True, parents=True)
    return cache_dirpath / f"{uuid}{image_format}"


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


def save_to_api(object_list: List[BaseModel]) -> None:
    """Convert bia_data_model to bia_integrator_api.model and persist to API"""

    for obj in object_list:
        api_obj = getattr(api_models, obj.model.type_name).model_validate_json(
            obj.model_dump_json()
        )
        # First try to retrieve object
        try:
            api_get_method = f"get_{to_snake(obj.model.type_name)}"
            api_copy_of_obj = getattr(api_client, api_get_method)(api_obj.uuid)
        except NotFoundException:
            api_copy_of_obj = None

        if api_obj == api_copy_of_obj:
            message = f"Not writing object with uuid: {obj.uuid} and type: {obj.model.type_name} to API because an identical copy of object exists in API"
            logger.warning(message)
            continue
        elif api_copy_of_obj:
            obj.version = api_copy_of_obj.version + 1

        api_creation_method = f"post_{to_snake(obj.model.type_name)}"
        getattr(api_client, api_creation_method)(api_obj)
        logger.debug(f"persisted {obj.uuid} of type {obj.model.type_name} to API")

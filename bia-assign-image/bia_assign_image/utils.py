from pathlib import Path
from uuid import UUID
from typing import Any, Callable, List
from bia_shared_datamodels import semantic_models
from bia_shared_datamodels.bia_data_model import DocumentMixin

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


def in_bioformats_single_file_formats_list(file_location: [Path | str]) -> bool:  # type: ignore
    """Check if ext of path/uri/name of file in bioformats single file formats list"""
    ext = get_image_extension(f"{file_location}")
    return extension_in_bioformats_single_file_formats_list(ext)


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


# Originally from bia-export
def get_all_api_results(
    uuid: UUID,
    api_method: Callable,
    page_size_setting: int = 20,
    aggregator_list: list[DocumentMixin] = None,
) -> list[DocumentMixin]:
    if not aggregator_list:
        aggregator_list = []
        start_uuid = None
    else:
        start_uuid = aggregator_list[-1].uuid

    fetched_objects = api_method(
        str(uuid),
        page_size=page_size_setting,
        start_from_uuid=str(start_uuid) if start_uuid else None,
    )
    aggregator_list += fetched_objects

    if len(fetched_objects) != page_size_setting:
        return aggregator_list
    else:
        return get_all_api_results(uuid, api_method, page_size_setting, aggregator_list)


def get_value_from_attribute_list(
    attribute_list: List[semantic_models.Attribute],
    attribute_name: str,
    default: Any = [],
) -> Any:
    """Get the value of named attribute from a list of attributes"""

    # Assumes attribute.value is a Dict
    return next(
        (
            attribute.value[attribute_name]
            for attribute in attribute_list
            if attribute.name == attribute_name
        ),
        default,
    )

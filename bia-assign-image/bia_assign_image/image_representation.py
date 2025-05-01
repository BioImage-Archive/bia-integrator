from pathlib import Path
from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation


def get_image_representation(
    accession_id: str,
    file_references: List[bia_data_model.FileReference],
    image: bia_data_model.Image,
    use_type: semantic_models.ImageRepresentationUseType,
    file_uri: str = "",
) -> bia_data_model.ImageRepresentation:
    # Note: we assume image_uuid is correct. I.e file references in image_uuid
    # match those passed into this function. We are only checking same
    # UUIDs are present, and not order or numbers
    file_reference_uuids_from_image = set(image.original_file_reference_uuid)
    file_reference_uuids_passed_to_func = set([f.uuid for f in file_references])
    assertion_error_msg = (
        "The FileReference UUIDs in Image "
        + f"{image.original_file_reference_uuid} do not match those of "
        + f"FileReferences {file_references} supplied to this function."
    )
    assert (
        file_reference_uuids_from_image == file_reference_uuids_passed_to_func
    ), assertion_error_msg

    if not isinstance(use_type, semantic_models.ImageRepresentationUseType):
        use_type = semantic_models.ImageRepresentationUseType(use_type.upper())

    total_size_in_bytes = 0
    attribute = []
    # Get image format. ATM convention is:
    #   - uploaded_by_submitter is decided by suffix
    #   - thumbnail and static display are png
    #   - interactive display is ome.zarr
    if use_type == semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        # TODO: Confirm convention below with BIA team i.e. csv of sorted unique image formats
        image_format_list = [get_image_extension(f.file_path) for f in file_references]
        image_format_set = set(image_format_list)
        image_format_list = list(image_format_set)
        image_format_list.sort()
        image_format = ",".join(image_format_list)

        # Sum size of all file references
        total_size_in_bytes = sum([f.size_in_bytes for f in file_references])

        # Copy file_pattern from image if it exists (only for UPLOADED_BY_SUBMITTER rep)
        file_pattern = next(
            (attr for attr in image.attribute if attr.name == "file_pattern"), None
        )
        if file_pattern:
            attribute.append(file_pattern)

    else:
        image_format_map = {
            semantic_models.ImageRepresentationUseType.THUMBNAIL: ".png",
            semantic_models.ImageRepresentationUseType.STATIC_DISPLAY: ".png",
            semantic_models.ImageRepresentationUseType.INTERACTIVE_DISPLAY: ".ome.zarr",
        }
        image_format = image_format_map[use_type]

    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image.uuid,
        image_format,
        # Note that using the Enum ImageRepresentation gives a different UUID than using its value
        use_type.value,
    )

    file_uri_list = []
    if file_uri == "":
        if use_type == semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
            file_uri_list.extend([f.uri for f in file_references])
    else:
        file_uri_list.append(file_uri)

    model_dict = {
        "uuid": image_representation_uuid,
        "version": 0,
        "use_type": use_type,
        "representation_of_uuid": image.uuid,
        "file_uri": file_uri_list,
        "total_size_in_bytes": total_size_in_bytes,
        "image_format": image_format,
    }

    model = bia_data_model.ImageRepresentation.model_validate(model_dict)
    model.attribute = attribute
    return model


# Copied from bia_converter_light.utils
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

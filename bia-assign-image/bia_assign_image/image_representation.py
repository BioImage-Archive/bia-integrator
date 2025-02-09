from pathlib import Path
from typing import List
from bia_assign_image.config import settings
from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation


def get_image_representation(
    accession_id: str,
    file_references: List[bia_data_model.FileReference,],
    image: bia_data_model.Image,
    use_type: semantic_models.ImageRepresentationUseType,
) -> bia_data_model.ImageRepresentation:
    # TODO: Put this is settings
    file_uri_base = f"{settings.endpoint_url.strip('/')}/{settings.bucket_name}"

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
    # Get image format. ATM convention is:
    #   - uploaded_by_submitter is decided by suffix
    #   - thumbnail and static display are png
    #   - interactive display is ome.zarr
    if use_type == semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        # TODO: Revisit this block of code when we start many file_refs->one_image
        assert len(file_references) == 1
        image_format = get_image_extension(file_references[0].file_path)
        total_size_in_bytes = file_references[0].size_in_bytes
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

    if use_type == semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        file_uri = file_references[0].uri
    else:
        file_uri = f"{file_uri_base}/{accession_id}/{image.uuid}/{image_representation_uuid}{image_format}"

    model_dict = {
        "uuid": image_representation_uuid,
        "version": 0,
        "use_type": use_type,
        "representation_of_uuid": image.uuid,
        "file_uri": [
            file_uri,
        ],
        "total_size_in_bytes": total_size_in_bytes,
        "image_format": image_format,
    }

    model = bia_data_model.ImageRepresentation.model_validate(model_dict)
    model.attribute = image.attribute
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

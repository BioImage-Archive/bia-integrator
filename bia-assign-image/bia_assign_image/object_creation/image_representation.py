from uuid import UUID
from pathlib import Path
from typing import List
from bia_shared_datamodels import (
    bia_data_model,
    semantic_models,
)
from bia_shared_datamodels.package_specific_uuid_creation import shared


def get_image_representation(
    study_uuid: UUID,
    file_references: List[bia_data_model.FileReference],
    image: bia_data_model.Image,
    file_uri: str = "",
    object_creator: semantic_models.Provenance = semantic_models.Provenance.bia_image_conversion,
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

    total_size_in_bytes = file_references[0].size_in_bytes
    additional_metadata = []
    file_uri_list = [
        file_references[0].uri,
    ]

    # Get image format. Assume this is determined by the file_uri. Except when dealing with uploaded by submitter representation
    # Assumption that if creator is bia_assign_image we are dealing with uploaded by submitter rep.
    image_format = get_image_extension(file_uri)
    if (
        file_uri == ""
        and object_creator == semantic_models.Provenance.bia_image_assignment
    ):
        # TODO: Confirm convention below with BIA team i.e. csv of sorted unique image formats
        image_format_list = [get_image_extension(f.file_path) for f in file_references]
        image_format_set = set(image_format_list)
        image_format_list = list(image_format_set)
        image_format_list.sort()
        image_format = ",".join(image_format_list)

        # Sum size of all file references
        total_size_in_bytes = sum([f.size_in_bytes for f in file_references])

        # Set file uri as list of uris of all file references
        file_uri_list = [f.uri for f in file_references]
    else:
        file_uri_list = [
            file_uri,
        ]

    # TODO: Discuss if we still want to do this after 2025_04 model change
    ## Copy file_pattern from image if it exists (only for UPLOADED_BY_SUBMITTER rep)
    # file_pattern = next(
    #    (attr for attr in image.attribute if attr.name == "file_pattern"), None
    # )
    # if file_pattern:
    #    attribute.append(file_pattern)

    if object_creator != semantic_models.Provenance.bia_image_assignment:
        raise Exception("object_creator must be bia_image_assignment")

    image_representation_uuid, image_representation_uuid_attribute = (
        shared.create_image_representation_uuid(
            study_uuid, image.uuid, semantic_models.Provenance.bia_image_assignment
        )
    )

    model_dict = {
        "uuid": image_representation_uuid,
        "version": 0,
        "representation_of_uuid": image.uuid,
        "file_uri": file_uri_list,
        "total_size_in_bytes": total_size_in_bytes,
        "image_format": image_format,
        "object_creator": object_creator,
        "additional_metadata": additional_metadata,
    }

    model_dict["additional_metadata"].append(
        image_representation_uuid_attribute.model_dump()
    )

    model = bia_data_model.ImageRepresentation.model_validate(model_dict)
    # model.attribute = attribute
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

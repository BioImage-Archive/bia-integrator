import logging

from uuid import UUID
from typing import List, Optional
from bia_shared_datamodels import (
    bia_data_model,
    semantic_models,
    uuid_creation,
    attribute_models,
)


logger = logging.getLogger()


# TODO: Explore just passing original_file_reference_uuid then deriving
#       other UUIDs from this.
def get_image(
    image_uuid: UUID,
    image_uuid_unique_string: str,
    submission_dataset_uuid: UUID,
    creation_process_uuid: UUID,
    file_references: List[bia_data_model.FileReference,],
    file_pattern: str | None = None,
) -> bia_data_model.Image:
    n_file_references = len(file_references)
    assert n_file_references > 0

    original_file_reference_uuid = [f.uuid for f in file_references]

    additional_metadata = []
    add_attributes_from_file_references(
        file_references=file_references, additional_metadata=additional_metadata
    )
    add_file_pattern_attribute(
        file_pattern=file_pattern,
        file_references=file_references,
        additional_metadata=additional_metadata,
    )
    add_uuid_unique_input_attribute(image_uuid_unique_string, additional_metadata)

    model_dict = {
        "uuid": image_uuid,
        "version": 0,
        "submission_dataset_uuid": submission_dataset_uuid,
        "creation_process_uuid": creation_process_uuid,
        "original_file_reference_uuid": original_file_reference_uuid,
        "object_creator": semantic_models.Provenance.bia_image_assignment,
        "additional_metadata": additional_metadata,
    }

    model = bia_data_model.Image.model_validate(model_dict)

    return model


def add_uuid_unique_input_attribute(
    image_uuid_unique_string: str, additional_metadata: list
) -> None:
    unique_string_dict = {
        "provenance": semantic_models.Provenance.bia_image_assignment,
        "name": "uuid_unique_input",
        "value": {
            "uuid_unique_input": image_uuid_unique_string,
        },
    }
    additional_metadata.append(
        attribute_models.DocumentUUIDUinqueInputAttribute.model_validate(
            unique_string_dict
        )
    )


def add_attributes_from_file_references(
    file_references: list[bia_data_model.FileReference], additional_metadata: list
) -> None:
    # Add attributes from file references
    for file_reference in file_references:
        for attribute in file_reference.additional_metadata:
            if attribute.name == "attributes_from_biostudies.File":
                new_attribute_dict = {
                    "provenance": semantic_models.Provenance.bia_image_assignment,
                    "name": f"attributes_from_file_reference_{file_reference.uuid}",
                    "value": attribute.value,
                }
                additional_metadata.append(
                    semantic_models.Attribute.model_validate(new_attribute_dict)
                )


def add_file_pattern_attribute(
    file_pattern: Optional[str],
    file_references: list[bia_data_model.FileReference],
    additional_metadata: list,
) -> None:
    # Add pattern to Image attribute - used to select file references for image conversion (e.g. time series)
    # At the moment we are only adding the first file in the list of file references.
    # TODO: Find out how to add pattern for selecting whole words with 'OR' in parse module. I.e. 'file path 1' or 'file path 2' or ...
    if not file_pattern:
        if len(file_references) > 1:
            message = (
                f"No file pattern received. Only the first file reference out of {n_file_references} "
                + "has been added to the file pattern."
            )
            logger.warning(message)
        file_pattern = file_references[0].file_path

    file_pattern_attr_dict = {
        "provenance": semantic_models.Provenance.bia_image_assignment,
        "name": "file_pattern",
        "value": {
            "file_pattern": file_pattern,
        },
    }
    additional_metadata.append(
        semantic_models.Attribute.model_validate(file_pattern_attr_dict)
    )


def create_image_uuid_unique_string(
    file_reference_uuids: List[UUID] | List[str],
) -> str:
    """Create the unique string used in generating uuids for bia_data_model.Image objects"""
    return " ".join([str(f) for f in sorted(file_reference_uuids)])

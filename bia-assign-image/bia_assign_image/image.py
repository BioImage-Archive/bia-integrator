import logging

from uuid import UUID
from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation


logger = logging.getLogger()


# TODO: Explore just passing original_file_reference_uuid then deriving
#       other UUIDs from this.
def get_image(
    submission_dataset_uuid: UUID,
    creation_process_uuid: UUID,
    file_references: List[bia_data_model.FileReference,],
    file_pattern: str | None = None,
) -> bia_data_model.Image:
    n_file_references = len(file_references)
    assert n_file_references > 0

    original_file_reference_uuid = [f.uuid for f in file_references]
    model_dict = {
        "version": 0,
        "submission_dataset_uuid": submission_dataset_uuid,
        "creation_process_uuid": creation_process_uuid,
        "original_file_reference_uuid": original_file_reference_uuid,
    }

    model_dict["uuid"] = uuid_creation.create_image_uuid(original_file_reference_uuid)
    model = bia_data_model.Image.model_validate(model_dict)

    # Add attributes from file references
    for file_reference in file_references:
        for attribute in file_reference.attribute:
            if (
                attribute.name == "attributes_from_biostudies.File"
                and "attributes" in attribute.value
            ):
                new_attribute_dict = {
                    "provenance": semantic_models.AttributeProvenance.bia_conversion,
                    "name": f"attributes_from_file_reference_{file_reference.uuid}",
                    "value": attribute.value,
                }
                model.attribute.append(
                    semantic_models.Attribute.model_validate(new_attribute_dict)
                )

    # Add pattern to Image attribute - used to select file references for image conversion (e.g. time series)
    # At the moment we are only adding the first file in the list of file references.
    # TODO: Find out how to add pattern for selecting whole words with 'OR' in parse module. I.e. 'file path 1' or 'file path 2' or ...
    if not file_pattern:
        if n_file_references > 1:
            message = (
                "No file pattern received. Only the first file reference out of {n_file_references} "
                + "has been added to the file pattern."
            )
            logger.warning(message)
        file_pattern = file_references[0].file_path

    file_pattern_attr_dict = {
        "provenance": semantic_models.AttributeProvenance.bia_conversion,
        "name": "file_pattern",
        "value": {
            "file_pattern": file_pattern,
        },
    }
    model.attribute.append(
        semantic_models.Attribute.model_validate(file_pattern_attr_dict)
    )

    return model

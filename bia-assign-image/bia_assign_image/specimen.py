from typing import List
from uuid import UUID
from bia_shared_datamodels import (
    bia_data_model,
    uuid_creation,
    semantic_models,
    attribute_models,
)


def get_specimen(
    study_uuid: UUID,
    image_uuid: UUID,
    imaging_preparation_protocol_uuid: List[UUID],
    sample_of_uuid: List[UUID],
) -> bia_data_model.Specimen:
    unique_string = str(image_uuid)
    model_dict = {
        "version": 0,
        "uuid": uuid_creation.create_specimen_uuid(study_uuid, unique_string),
        "imaging_preparation_protocol_uuid": imaging_preparation_protocol_uuid,
        "sample_of_uuid": sample_of_uuid,
        "object_creator": semantic_models.Provenance.bia_image_assignment,
        "additional_metadata": [],
    }
    unique_string_dict = {
        "provenance": semantic_models.Provenance.bia_image_assignment,
        "name": "uuid_unique_input",
        "value": {
            "uuid_unique_input": unique_string,
        },
    }
    model_dict["additional_metadata"].append(
        attribute_models.DocumentUUIDUinqueInputAttribute.model_validate(
            unique_string_dict
        )
    )

    return bia_data_model.Specimen.model_validate(model_dict)

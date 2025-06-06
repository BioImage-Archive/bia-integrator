from uuid import UUID
from typing import Optional
from bia_shared_datamodels import (
    bia_data_model,
    uuid_creation,
    semantic_models,
    attribute_models,
)


def get_creation_process(
    study_uuid: UUID,
    output_image_uuid: UUID,
    subject_specimen_uuid: Optional[UUID] = None,
    image_acquisition_protocol_uuid: list[UUID] = [],
    input_image_uuid: list[UUID] = [],
    annotation_method_uuid: list[UUID]  = [],
    protocol_uuid: list[UUID] = [],
) -> bia_data_model.CreationProcess:
    unique_string = str(output_image_uuid)

    model_dict = {
        "version": 0,
        "uuid": uuid_creation.create_creation_process_uuid(study_uuid, unique_string),
        "object_creator": semantic_models.Provenance.bia_image_assignment,
        "additional_metadata": [],
        "subject_specimen_uuid": subject_specimen_uuid,
        "image_acquisition_protocol_uuid": image_acquisition_protocol_uuid,
        "input_image_uuid": input_image_uuid,
        "annotation_method_uuid": annotation_method_uuid,
        "protocol_uuid": protocol_uuid,
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

    # TODO: Discuss 'Protocol' with FR and TZ - where do we get this from?

    return bia_data_model.CreationProcess.model_validate(model_dict)

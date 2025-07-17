from uuid import UUID
from typing import Optional
from bia_shared_datamodels import (
    bia_data_model,
    semantic_models,
)
from bia_shared_datamodels.package_specific_uuid_creation import shared


def get_creation_process(
    study_uuid: UUID,
    output_image_uuid: UUID,
    subject_specimen_uuid: Optional[UUID] = None,
    image_acquisition_protocol_uuid: list[UUID] = [],
    input_image_uuid: list[UUID] = [],
    annotation_method_uuid: list[UUID] = [],
    protocol_uuid: list[UUID] = [],
) -> bia_data_model.CreationProcess:

    uuid, uuid_attribute = shared.create_creation_process_uuid(
        study_uuid,
        output_image_uuid,
        semantic_models.Provenance.bia_image_assignment,
    )

    model_dict = {
        "version": 0,
        "uuid": uuid,
        "object_creator": semantic_models.Provenance.bia_image_assignment,
        "additional_metadata": [uuid_attribute.model_dump()],
        "subject_specimen_uuid": subject_specimen_uuid,
        "image_acquisition_protocol_uuid": image_acquisition_protocol_uuid,
        "input_image_uuid": input_image_uuid,
        "annotation_method_uuid": annotation_method_uuid,
        "protocol_uuid": protocol_uuid,
    }

    # TODO: Discuss 'Protocol' with FR and TZ - where do we get this from?

    return bia_data_model.CreationProcess.model_validate(model_dict)

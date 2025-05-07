from uuid import UUID
from typing import Optional, List
from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models


def get_creation_process(
    study_uuid: UUID,
    output_image_uuid: UUID,
    subject_specimen_uuid: Optional[UUID | None] = None,
    image_acquisition_protocol_uuid: Optional[List[UUID] | List] = [],
    input_image_uuid: Optional[List[UUID] | List] = [],
) -> bia_data_model.CreationProcess:
    model_dict = {
        "version": 0,
        "uuid": uuid_creation.create_creation_process_uuid(
            study_uuid, str(output_image_uuid)
        ),
        "object_creator": semantic_models.Provenance.bia_image_assignment,
    }
    if subject_specimen_uuid:
        model_dict["subject_specimen_uuid"] = subject_specimen_uuid
    if image_acquisition_protocol_uuid:
        model_dict["image_acquisition_protocol_uuid"] = image_acquisition_protocol_uuid
    if input_image_uuid:
        model_dict["input_image_uuid"] = input_image_uuid

    # TODO: Discuss 'Protocol' with FR and TZ - where do we get this from?

    return bia_data_model.CreationProcess.model_validate(model_dict)

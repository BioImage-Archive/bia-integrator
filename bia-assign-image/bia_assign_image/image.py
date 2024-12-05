from uuid import UUID
from typing import List
from bia_shared_datamodels import bia_data_model, uuid_creation

# TODO: Explore just passing original_file_reference_uuid then deriving
#       other UUIDs from this.
def get_image(
        submission_dataset_uuid: UUID,
        creation_process_uuid: UUID,
        original_file_reference_uuid: List[UUID,],
    ) -> bia_data_model.Image:
    image_dict = {
        "version": 0,
        "submission_dataset_uuid": submission_dataset_uuid,
        "creation_process_uuid": creation_process_uuid,
        "original_file_reference_uuid": original_file_reference_uuid,
    }
    image_dict["uuid"] = uuid_creation.create_image_uuid(
        original_file_reference_uuid
    )
    # TODO: Add attributes from each file reference

    return bia_data_model.Image.model_validate(image_dict)

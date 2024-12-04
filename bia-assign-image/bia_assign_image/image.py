from bia_shared_datamodels import bia_data_model, uuid_creation

def get_image(submission_dataset_uuid, creation_process_uuid, original_file_reference_uuid):
    image_dict = {
        "version": 0,
        "submission_dataset_uuid": submission_dataset_uuid,
        "creation_process_uuid": creation_process_uuid,
        "original_file_reference_uuid": original_file_reference_uuid,
    }
    image_dict["uuid"] = uuid_creation.create_image_uuid(
        original_file_reference_uuid
    )

    return bia_data_model.Image.model_validate(image_dict)

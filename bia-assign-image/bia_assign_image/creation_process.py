from uuid import UUID
from bia_shared_datamodels import bia_data_model, uuid_creation

def get_creation_process(
        input_image_uuid: UUID,
        dataset: bia_data_model.Dataset,
        subject_specimen_uuid: UUID,
    ) -> bia_data_model.CreationProcess:

    model_dict = {
        "version": 0,
        "uuid": uuid_creation.create_creation_process_uuid(input_image_uuid),
        "input_image_uuid": [input_image_uuid,],
        "subject_specimen_uuid": subject_specimen_uuid,
    }
    attribute_names = (
        ("image_acquisition_protocol_uuid", "image_acquisition_protocol_uuid",),
    )
    for attribute_name, mapped_name in attribute_names:
        model_dict[mapped_name] = next(
        (
            attribute.value[attribute_name]
            for attribute in dataset.attribute
            if attribute.name == attribute_name
        ),
        []
        )

    return bia_data_model.CreationProcess.model_validate(model_dict)

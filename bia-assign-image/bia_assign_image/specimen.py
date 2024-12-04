from bia_ingest.persistence_strategy import PersistenceStrategy
from bia_shared_datamodels import bia_data_model, uuid_creation

def get_specimen(image:bia_data_model.Image, persister: PersistenceStrategy) -> bia_data_model.Specimen:

    model_dict = {
        "version": 0,
        "uuid": uuid_creation.create_specimen_uuid(image.uuid),
    }

    dataset = persister.fetch_by_uuid(
        [image.submission_dataset_uuid,],
        bia_data_model.Dataset
        )[0]
    attribute_names = (
        (
            "specimen_imaging_preparation_protocol_uuid",
            "imaging_preparation_protocol_uuid",
        ),
        (
            "bio_sample_uuid",
            "sample_of_uuid",
        ),
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
    return bia_data_model.Specimen.model_validate(model_dict)

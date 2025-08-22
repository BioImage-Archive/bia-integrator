from bia_shared_datamodels.uuid_creation import (
    create_dataset_uuid,
    create_file_reference_uuid,
    create_image_uuid,
    create_image_representation_uuid,
    create_specimen_uuid,
    create_bio_sample_uuid,
    create_study_uuid,
    create_protocol_uuid,
    create_annotation_method_uuid,
    create_image_acquisition_protocol_uuid,
    create_specimen_imaging_preparation_protocol_uuid,
    create_creation_process_uuid,
)
from bia_shared_datamodels.bia_data_model import (
    Dataset,
    FileReference,
    Image,
    ImageRepresentation,
    Specimen,
    BioSample,
    Study,
    Protocol,
    ImageAcquisitionProtocol,
    SpecimenImagingPreparationProtocol,
    AnnotationMethod,
    CreationProcess,
)

if __name__ == "__main__":
    study_uuid = None
    type = AnnotationMethod
    accession_id = "S-BIAD-TEST-ASSIGN-IMAGE"
    unique_string = "Template Annotation Dataset"

    study_uuid = create_study_uuid(accession_id)

    if type == Study:
        uuid = study_uuid
    elif type == Dataset:
        uuid = create_dataset_uuid(study_uuid, unique_string)
    elif type == FileReference:
        uuid = create_file_reference_uuid(study_uuid, unique_string)
    elif type == Image:
        uuid = create_image_uuid(study_uuid, unique_string)
    elif type == ImageRepresentation:       
        uuid = create_image_representation_uuid(study_uuid, unique_string)
    elif type == Specimen:
        uuid = create_specimen_uuid(study_uuid, unique_string)
    elif type == BioSample:
        uuid = create_bio_sample_uuid(study_uuid, unique_string)
    elif type == Protocol:
        uuid = create_protocol_uuid(study_uuid, unique_string)
    elif type == ImageAcquisitionProtocol:
        uuid = create_image_acquisition_protocol_uuid(study_uuid, unique_string)
    elif type == SpecimenImagingPreparationProtocol:
        uuid = create_specimen_imaging_preparation_protocol_uuid(study_uuid, unique_string)
    elif type == AnnotationMethod:
        uuid = create_annotation_method_uuid(study_uuid, unique_string)
    elif type == CreationProcess:
        uuid = create_creation_process_uuid(study_uuid, unique_string)


    print(uuid)
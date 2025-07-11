from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference


def convert_creation_process(
    creation_process: ROCrateModels.CreationProcess,
    study_uuid: str,
) -> APIModels.CreationProcess:

    annotation_method_uuid = []
    image_acquisition_protocol_uuid = []
    input_image_uuid = []
    protocol_uuid = []

    if creation_process.annotationMethod and len(creation_process.annotationMethod) > 0:
        annotation_method_uuid = create_uuid_list(
            creation_process.annotationMethod,
            uuid_creation.create_annotation_method_uuid,
            study_uuid,
        )

    if (
        creation_process.imageAcquisitionProtocol
        and len(creation_process.imageAcquisitionProtocol) > 0
    ):
        image_acquisition_protocol_uuid = create_uuid_list(
            creation_process.imageAcquisitionProtocol,
            uuid_creation.create_image_acquisition_protocol_uuid,
            study_uuid,
        )

    if creation_process.protocol and len(creation_process.protocol) > 0:
        image_acquisition_protocol_uuid = create_uuid_list(
            creation_process.protocol,
            uuid_creation.create_protocol_uuid,
            study_uuid,
        )

    if creation_process.inputImage and len(creation_process.inputImage) > 0:
        input_image_uuid = create_uuid_list(
            creation_process.inputImage,
            uuid_creation.create_image_uuid,
            study_uuid,
        )

    subject_specimen_uuid = None
    if creation_process.subject:
        subject_specimen_uuid = str(
            uuid_creation.create_specimen_uuid(study_uuid, creation_process.subject.id)
        )

    creation_process = {
        "uuid": str(
            uuid_creation.create_creation_process_uuid(study_uuid, creation_process.id)
        ),
        "version": 0,
        "annotation_method_uuid": annotation_method_uuid,
        "subject_specimen_uuid": subject_specimen_uuid,
        "image_acquisition_protocol_uuid": image_acquisition_protocol_uuid,
        "protocol_uuid": protocol_uuid,
        "input_image_uuid": input_image_uuid,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [
            AttributeModels.DocumentUUIDUinqueInputAttribute(
                provenance=APIModels.Provenance.BIA_INGEST,
                name="uuid_unique_input",
                value={"uuid_unique_input": creation_process.id},
            ).model_dump()
        ],
    }

    return APIModels.CreationProcess(**creation_process)


def create_uuid_list(
    object_id_list: list[ObjectReference],
    uuid_creation_function: callable,
    study_uuid: str,
):

    return [
        str(uuid_creation_function(study_uuid, obj_id.id)) for obj_id in object_id_list
    ]

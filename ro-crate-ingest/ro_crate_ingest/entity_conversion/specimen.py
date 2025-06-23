from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
import bia_shared_datamodels.attribute_models as AttributeModels
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference


def create_api_specimen(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.Protocol]:
    ro_crate_specimen = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Specimen)
    )

    specimen_list = []
    for specimen in ro_crate_specimen:
        specimen_list.append(convert_specimen(specimen, study_uuid))

    return specimen_list


def convert_specimen(
    specimen: ROCrateModels.Specimen,
    study_uuid: str,
) -> APIModels.CreationProcess:

    sample_of_uuid = []
    imaging_preparation_protocol_uuid = []

    if specimen.biologicalEntity and len(specimen.biologicalEntity) > 0:
        sample_of_uuid = create_uuid_list(
            specimen.biologicalEntity,
            uuid_creation.create_bio_sample_uuid,
            study_uuid,
        )

    if (
        specimen.imagingPreparationProtocol
        and len(specimen.imagingPreparationProtocol) > 0
    ):
        imaging_preparation_protocol_uuid = create_uuid_list(
            specimen.imagingPreparationProtocol,
            uuid_creation.create_specimen_imaging_preparation_protocol_uuid,
            study_uuid,
        )

    specimen = {
        "uuid": str(uuid_creation.create_specimen_uuid(study_uuid, specimen.id)),
        "version": 0,
        "sample_of_uuid": sample_of_uuid,
        "imaging_preparation_protocol_uuid": imaging_preparation_protocol_uuid,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [
            AttributeModels.DocumentUUIDUinqueInputAttribute(
                provenance=APIModels.Provenance.BIA_INGEST,
                name="uuid_unique_input",
                value={"uuid_unique_input": specimen.id},
            ).model_dump()
        ],
    }

    return APIModels.Specimen(**specimen)


def create_uuid_list(
    object_id_list: list[ObjectReference],
    uuid_creation_function: callable,
    study_uuid: str,
):

    return [
        str(uuid_creation_function(study_uuid, obj_id.id)) for obj_id in object_id_list
    ]

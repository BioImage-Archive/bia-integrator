from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.attribute_models as AttributeModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import logging

logger = logging.getLogger("__main__." + __name__)


def create_api_image_acquisition_protocol(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.AnnotationMethod]:
    ro_crate_annotation_method = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.AnnotationMethod)
    )

    annotation_method_list = []
    for annotation_method in ro_crate_annotation_method:
        annotation_method_list.append(
            convert_annotation_method(annotation_method, study_uuid)
        )

    return annotation_method_list


def convert_annotation_method(
    ro_crate_annotation_method: ROCrateModels.AnnotationMethod,
    study_uuid: str,
) -> APIModels.AnnotationMethod:
    
    method_type = []
    for mt in ro_crate_annotation_method.methodType:
        method_type.append(mt.replace(" ", "_").lower())

    iap = {
        "uuid": str(uuid_creation.create_annotation_method_uuid(
            study_uuid, ro_crate_annotation_method.id
        )),
        "title": ro_crate_annotation_method.title,
        "protocol_description": ro_crate_annotation_method.protocolDescription,
        "annotation_criteria": ro_crate_annotation_method.annotationCriteria,
        "annotation_coverage": ro_crate_annotation_method.annotationCoverage,
        "method_type": method_type,
        "annotation_source_indicator": ro_crate_annotation_method.annotationSourceIndicator,
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [
            AttributeModels.DocumentUUIDUinqueInputAttribute(
                provenance=APIModels.Provenance.BIA_INGEST,
                name="uuid_unique_input",
                value={"uuid_unique_input": ro_crate_annotation_method.id},
            ).model_dump()
        ],
    }

    return APIModels.AnnotationMethod(**iap)

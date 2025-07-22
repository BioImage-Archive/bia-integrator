from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import logging
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_bio_sample_uuid,
)

logger = logging.getLogger("__main__." + __name__)


def create_api_bio_sample(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.BioSample]:
    ro_crate_bio_sample = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.BioSample)
    )

    bio_sample_list = []
    for bio_sample in ro_crate_bio_sample:
        bio_sample_list.append(
            convert_bio_sample(bio_sample, crate_objects_by_id, study_uuid)
        )

    return bio_sample_list


def convert_bio_sample(
    ro_crate_bio_sample: ROCrateModels.BioSample,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
) -> APIModels.BioSample:

    taxons = []
    for taxon_reference in ro_crate_bio_sample.organismClassification:
        taxons.append(convert_taxon(crate_objects_by_id[taxon_reference.id]))

    uuid, uuid_attribute = create_bio_sample_uuid(study_uuid, ro_crate_bio_sample.id)

    bio_sample = {
        "uuid": str(uuid),
        "title": ro_crate_bio_sample.id,
        "version": 0,
        "organism_classification": taxons,
        "biological_entity_description": ro_crate_bio_sample.biologicalEntityDescription,
        "intrinsic_variable_description": ro_crate_bio_sample.intrinsicVariableDescription,
        "extrinsic_variable_description": ro_crate_bio_sample.extrinsicVariableDescription,
        "experimental_variable_description": ro_crate_bio_sample.experimentalVariableDescription,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [uuid_attribute.model_dump()],
    }

    return APIModels.BioSample(**bio_sample)


def convert_taxon(ro_crate_taxon: ROCrateModels.Taxon) -> APIModels.Taxon:
    taxon = {
        "common_name": ro_crate_taxon.commonName,
        "scientific_name": ro_crate_taxon.scientificName,
        "additional_metadata": [],
    }

    if ro_crate_taxon.id.startswith("NCBITaxon:"):
        taxon["id"] = ro_crate_taxon.id

    return APIModels.Taxon(**taxon)

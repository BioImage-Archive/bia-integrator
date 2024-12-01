from .mock_growth_protocol import (
    get_growth_protocol_as_map,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from .utils import accession_id


def get_bio_sample_as_map() -> dict[str, bia_data_model.BioSample]:
    # For UUID
    attributes_to_consider_for_uuid = [
        "accession_id",
        "accno",
        "title_id",
        "organism_classification",
        "biological_entity_description",
        "intrinsic_variable_description",
        "extrinsic_variable_description",
        "experimental_variable_description",
        "growth_protocol_uuid",
    ]

    growth_protocol_map = get_growth_protocol_as_map()

    taxon1 = semantic_models.Taxon.model_validate(
        {
            "common_name": "human",
            "scientific_name": "Homo sapiens",
            "ncbi_id": None,
        }
    )
    taxon2 = semantic_models.Taxon.model_validate(
        {
            "common_name": "mouse",
            "scientific_name": "Mus musculus",
            "ncbi_id": None,
        }
    )
    biosample_info = {
        "Test Biosample 1.Test specimen 1": {
            "accno": "Biosample-1",
            "accession_id": accession_id,
            "title_id": "Test Biosample 1",
            "organism_classification": [
                taxon1.model_dump(),
            ],
            "biological_entity_description": "Test biological entity 1",
            "experimental_variable_description": [
                "Test experimental entity 1",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 1",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 1\nwith escaped character",
            ],
            "version": 0,
            "growth_protocol_uuid": growth_protocol_map[
                "Test specimen 1.growth_protocol"
            ].uuid,
        },
        "Test Biosample 2 .Test specimen 1": {
            "accno": "Biosample-2",
            "accession_id": accession_id,
            "title_id": "Test Biosample 2 ",
            "organism_classification": [
                taxon2.model_dump(),
            ],
            "biological_entity_description": "Test biological entity 2",
            "experimental_variable_description": [
                "Test experimental entity 2",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 2",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 2",
            ],
            "version": 0,
            "growth_protocol_uuid": growth_protocol_map[
                "Test specimen 1.growth_protocol"
            ].uuid,
        },
        "Test Biosample 2 .Test specimen 2": {
            "accno": "Biosample-2",
            "accession_id": accession_id,
            "title_id": "Test Biosample 2 ",
            "organism_classification": [
                taxon2.model_dump(),
            ],
            "biological_entity_description": "Test biological entity 2",
            "experimental_variable_description": [
                "Test experimental entity 2",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 2",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 2",
            ],
            "version": 0,
            "growth_protocol_uuid": growth_protocol_map[
                "Test specimen 2.growth_protocol"
            ].uuid,
        },
    }

    biosample_objects = {}
    for key, bio_sample in biosample_info.items():
        bio_sample["uuid"] = dict_to_uuid(bio_sample, attributes_to_consider_for_uuid)
        bio_sample.pop("accno")
        bio_sample.pop("accession_id")
        biosample_objects[key] = bia_data_model.BioSample.model_validate(bio_sample)

    return biosample_objects

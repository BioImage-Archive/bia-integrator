from .mock_growth_protocol import (
    get_growth_protocol_as_map,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_bio_sample_uuid
from .mock_object_constants import study_uuid


def get_bio_sample_as_map() -> dict[str, bia_data_model.BioSample]:
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
    # A biosample incorporates growth protocols which come from
    # Biostudies 'Specimen' sections (NOT bia_data_model.Specimen)
    # To account for the possible combinations, the growth protocol
    # uuids are incorporated into the BioSample uuid_unique_inputs
    growth_protocol_specimen_1_uuid = growth_protocol_map[
        "Test specimen 1.growth_protocol"
    ].uuid
    growth_protocol_specimen_2_uuid = growth_protocol_map[
        "Test specimen 2.growth_protocol"
    ].uuid

    title_id_1 = "Test Biosample 1"
    unique_string_biosample1_specimen1 = (
        f"Biosample-1 {growth_protocol_specimen_1_uuid}"
    )
    title_id_2 = "Test Biosample 2 "
    unique_string_biosample2_specimen1 = (
        f"Biosample-2 {growth_protocol_specimen_1_uuid}"
    )
    unique_string_biosample2_specimen2 = (
        f"Biosample-2 {growth_protocol_specimen_2_uuid}"
    )
    biosample_info = {
        "Test Biosample 1.Test specimen 1": {
            "uuid": create_bio_sample_uuid(
                study_uuid, unique_string_biosample1_specimen1
            ),
            "title": title_id_1,
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
            "growth_protocol_uuid": growth_protocol_specimen_1_uuid,
            "object_creator": semantic_models.Provenance.bia_ingest,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance.bia_ingest,
                    "name": "uuid_unique_input",
                    "value": {
                        "uuid_unique_input": unique_string_biosample1_specimen1,
                    },
                }
            ],
        },
        "Test Biosample 2 .Test specimen 1": {
            "uuid": create_bio_sample_uuid(
                study_uuid, unique_string_biosample2_specimen1
            ),
            "title": title_id_2,
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
            "growth_protocol_uuid": growth_protocol_specimen_1_uuid,
            "object_creator": semantic_models.Provenance.bia_ingest,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance.bia_ingest,
                    "name": "uuid_unique_input",
                    "value": {
                        "uuid_unique_input": unique_string_biosample2_specimen1,
                    },
                }
            ],
        },
        "Test Biosample 2 .Test specimen 2": {
            "uuid": create_bio_sample_uuid(
                study_uuid, unique_string_biosample2_specimen2
            ),
            "title": title_id_2,
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
            "growth_protocol_uuid": growth_protocol_specimen_2_uuid,
            "object_creator": semantic_models.Provenance.bia_ingest,
            "additional_metadata": [
                {
                    "provenance": semantic_models.Provenance.bia_ingest,
                    "name": "uuid_unique_input",
                    "value": {
                        "uuid_unique_input": unique_string_biosample2_specimen2,
                    },
                }
            ],
        },
    }

    biosample_objects = {}
    for key, bio_sample in biosample_info.items():
        biosample_objects[key] = bia_data_model.BioSample.model_validate(bio_sample)

    return biosample_objects

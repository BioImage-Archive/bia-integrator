from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
import bia_shared_datamodels.ro_crate_models as ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld import LDModel, ROCrateModel
from rdflib.graph import Graph
from rdflib.namespace import RDF, OWL
from pathlib import Path
import inspect
from typing import Type
import json
from rocrate.rocrate import read_metadata
from rocrate_validator import services, models
import pyld


def test_ro_crate_used_terms_are_defined(
    bia_ontology: Graph, related_ontologies: Graph
):

    combined_ontology = bia_ontology + related_ontologies
    ontology_classes = [str(x) for x in combined_ontology.subjects(RDF.type, OWL.Class)]

    ro_crate_pydantic_models = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models",
    )

    for class_name, ldclass in ro_crate_pydantic_models:
        ldclass: Type[LDModel.LDModel]

        ldclass.validate_ontology_field_consistency(combined_ontology)

        assert ldclass.model_config["model_type"] in ontology_classes


def test_ro_crate_context_is_used_in_example(path_to_example_ro_crate):

    metadata_json = path_to_example_ro_crate / "ro-crate-metadata.json"

    prefixes = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "schema": "http://schema.org/",
        "dc": "http://purl.org/dc/terms/",
        "bia": "http://bia/",
    }

    context = SimpleJSONLDContext(prefixes=prefixes)

    ro_crate_pydantic_models = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_ro_crate.ro_crate_to_bia.ingest_models",
    )

    for name, ldclass in ro_crate_pydantic_models:
        for field_term in ldclass.generate_field_context():
            context.add_term(field_term)

    with open(metadata_json) as file:
        json_data = file.read()

    ro_crate_context = json.loads(json_data)["@context"]

    embedded_context = {}
    if isinstance(ro_crate_context, list):
        for context_item in ro_crate_context:
            if isinstance(context_item, dict):
                embedded_context |= context_item

    # NB: testing if all the terms we expect have the context we expect
    # Users are free to add their own additional terms, which we aim to process into attribute values eventually
    # Therefore not checking for exact equality
    for key, value in context.to_dict().items():
        assert embedded_context[key] == value


def test_example_ro_crate_is_valid_ro_crate(path_to_example_ro_crate):

    settings = services.ValidationSettings(
        rocrate_uri=path_to_example_ro_crate,
        profile_identifier="ro-crate-1.1",
        requirement_severity=models.Severity.REQUIRED,
    )

    result = services.validate(settings)

    assert not result.has_issues()

    read_metadata(path_to_example_ro_crate / "ro-crate-metadata.json")


def test_objects_in_example_ro_crate_match_pydantic_models(
    path_to_example_ro_crate: Path,
):

    metadata_json = path_to_example_ro_crate / "ro-crate-metadata.json"

    with open(metadata_json) as file:
        metadata = json.load(file)

    entities = metadata.get("@graph", [])
    context = metadata.get("@context", {})

    classes = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models",
    )

    def expand_entity(entity: dict, context: dict) -> str:
        document = {"@context": context, "@graph": [entity]}
        expanded = pyld.jsonld.expand(document)
        return expanded[0]

    for entity in entities:
        type_to_process = None
        entity_types = expand_entity(entity, context).get("@type")

        for name, model in classes:
            if model.model_config["model_type"] in entity_types:
                type_to_process = model
                break

        if type_to_process:
            type_to_process.model_validate(entity)
        elif "ro-crate-metadata.json" == entity.get("@id"):
            # This is the self-referencing ro-crate metadata object, which we don't currently need to process
            continue
        elif str(RDF.Property) in entity_types:
            # Users can define their own properties, which we currently do not not process
            continue
        else:
            raise ValueError(
                f"Entity {entity.get('@id')} of type {entity_types} does not match any known model."
            )

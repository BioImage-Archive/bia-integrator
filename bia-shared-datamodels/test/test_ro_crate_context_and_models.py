from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
import bia_shared_datamodels.ro_crate_models as ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld import LDModel
from rdflib.graph import Graph
from rdflib.namespace import RDF, OWL
from pathlib import Path
import inspect
from typing import Type
import json
from rocrate.rocrate import read_metadata
from rocrate_validator import services, models

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
        profile_identifier='ro-crate-1.1',
        requirement_severity=models.Severity.REQUIRED,
    )

    result = services.validate(settings)
    
    assert not result.has_issues()
    
    read_metadata(path_to_example_ro_crate / "ro-crate-metadata.json")


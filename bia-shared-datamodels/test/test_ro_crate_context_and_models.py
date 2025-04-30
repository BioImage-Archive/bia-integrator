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


def test_ro_crate_context_is_used_in_example():

    crate_path = (
        Path(__file__).parents[1]
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / "S-BIAD1494"
    )

    metadata_json = crate_path / "ro-crate-metadata.json"

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
        for field_term in ldclass.generate_field_context(compacted_ids=True):
            context.add_term(field_term)

    with open(metadata_json) as file:
        json_data = file.read()

    ro_crate_context = json.loads(json_data)["@context"]

    # NB: testing if all the terms we expect have the context we expect
    # Users are free to add their own additional terms, which we aim to process into attribute values eventually
    # Therefore not checking for exact equality
    for key, value in context.to_dict().items():
        assert ro_crate_context[key] == value

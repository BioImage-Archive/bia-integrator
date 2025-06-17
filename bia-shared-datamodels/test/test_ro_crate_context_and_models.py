from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
import bia_shared_datamodels.ro_crate_models as ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld import LDModel, ROCrateModel
from rdflib.graph import Graph
from rdflib.namespace import RDF, OWL, RDFS
from pathlib import Path
import inspect
from typing import Type
import json
from rocrate.rocrate import read_metadata
from rocrate_validator import services, models
import pyld
import pytest
import urllib
import requests


def test_ro_crate_used_terms_are_defined(
    bia_ontology: Graph, related_ontologies: Graph
):

    combined_ontology = bia_ontology + related_ontologies
    ontology_classes = [
        str(x) for x in combined_ontology.subjects(RDF.type, OWL.Class)
    ] + [str(x) for x in combined_ontology.subjects(RDF.type, RDFS.Class)]

    ro_crate_pydantic_models = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models"
        and issubclass(member, ROCrateModel.ROCrateModel),
    )

    for class_name, ldclass in ro_crate_pydantic_models:
        ldclass: Type[LDModel.LDModel]

        ldclass.validate_ontology_field_consistency(combined_ontology)

        assert ldclass.model_config["model_type"] in ontology_classes


@pytest.mark.parametrize(
    "path_to_example_ro_crate",
    ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"],
    indirect=True,
)
def test_ro_crate_context_is_used_in_example(path_to_example_ro_crate):

    metadata_json = path_to_example_ro_crate / "ro-crate-metadata.json"

    prefixes = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "schema": "http://schema.org/",
        "dc": "http://purl.org/dc/terms/",
        "bia": "http://bia/",
        "csvw": "http://www.w3.org/ns/csvw#",
    }

    context = SimpleJSONLDContext(prefixes=prefixes)

    ro_crate_pydantic_models = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models"
        and issubclass(member, ROCrateModel.ROCrateModel),
    )

    for name, ldclass in ro_crate_pydantic_models:
        for field_term in ldclass.generate_field_context():
            context.add_term(field_term)

    with open(metadata_json) as file:
        json_data = file.read()

    ro_crate_context = json.loads(json_data)["@context"]

    embedded_ro_crate_document_context = {}
    if isinstance(ro_crate_context, list):
        for context_item in ro_crate_context:
            if isinstance(context_item, dict):
                embedded_ro_crate_document_context |= context_item

    # NB: testing if all the terms we expect have the context we expect
    # Users are free to add their own additional terms, which we aim to process into attribute values eventually
    # Therefore not checking for exact equality
    for key, value in context.to_dict().items():
        assert embedded_ro_crate_document_context[key] == value


@pytest.mark.parametrize(
    "path_to_example_ro_crate",
    ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"],
    indirect=True,
)
def test_example_ro_crate_is_valid_ro_crate(path_to_example_ro_crate):

    settings = services.ValidationSettings(
        rocrate_uri=path_to_example_ro_crate,
        profile_identifier="ro-crate-1.1",
        requirement_severity=models.Severity.REQUIRED,
    )

    result = services.validate(settings)

    assert not result.has_issues()

    read_metadata(path_to_example_ro_crate / "ro-crate-metadata.json")


@pytest.mark.parametrize(
    "path_to_example_ro_crate",
    ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"],
    indirect=True,
)
def test_objects_in_example_ro_crate_match_pydantic_models(
    path_to_example_ro_crate: Path,
):

    metadata_json = path_to_example_ro_crate / "ro-crate-metadata.json"

    with open(metadata_json) as file:
        metadata = json.load(file)

    entities = metadata.get("@graph", [])
    context = metadata.get("@context", {})

    # Loading context from url once, to avoid multiple requests
    loaded_context = {}
    for item in context:
        if isinstance(item, str) and urllib.parse.urlparse(item):
            loaded_context |= requests.get(item).json().get("@context", {})
        elif isinstance(item, dict):
            loaded_context |= item

    classes = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models"
        and issubclass(member, ROCrateModel.ROCrateModel),
    )

    def expand_entity(entity: dict, context: dict) -> str:
        document = {"@context": context, "@graph": [entity]}
        expanded = pyld.jsonld.expand(document)
        return expanded[0]

    for entity in entities:
        type_to_process = None
        entity_types = expand_entity(entity, loaded_context).get("@type")

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

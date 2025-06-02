from rdflib.graph import Graph
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def bia_ontology():
    bia_ontology = Graph()
    bia_ontology.parse(
        str(
            Path(__file__).parents[1]
            / "src"
            / "bia_shared_datamodels"
            / "linked_data"
            / "bia_ontology.ttl"
        )
    )

    return bia_ontology


@pytest.fixture(scope="session")
def related_ontologies():
    rdf = Graph()
    rdf.parse("https://www.w3.org/1999/02/22-rdf-syntax-ns#")

    schema = Graph()
    schema.parse("https://schema.org/version/latest/schemaorg-current-http.ttl")

    dc = Graph()
    dc.parse(
        "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl"
    )

    return schema + dc + rdf


@pytest.fixture()
def path_to_example_ro_crate(request: pytest.FixtureRequest) -> Path:
    return (
        Path(__file__).parents[1]
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / request.param
    )

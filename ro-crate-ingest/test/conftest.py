from rdflib.graph import Graph
from pathlib import Path
import pytest
import os
from dotenv import dotenv_values
from bia_integrator_api.util import get_client


def pytest_configure(config: pytest.Config):
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["bia_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["bia_api_username"] = env_settings["local_bia_api_username"]
    os.environ["bia_api_password"] = env_settings["local_bia_api_password"]


@pytest.fixture(scope="session")
def tmp_bia_data_dir(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("bia_data_dir")
    os.environ["bia_data_dir"] = str(tmp_dir)
    return tmp_dir


@pytest.fixture()
def get_bia_api_client():
    return get_client(os.environ.get("bia_api_basepath"))


@pytest.fixture(scope="session")
def bia_ontology():
    bia_ontology = Graph()
    bia_ontology.parse(
        str(Path(__file__).parents[1] / "bia_ro_crate" / "model" / "bia_ontology.ttl")
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

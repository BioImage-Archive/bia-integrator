from rdflib.graph import Graph
from pathlib import Path
import pytest
import os
import json
from persistence.utils import create_test_user, set_dev_settings_to_local
from persistence.bia_api_client import BIAAPIClient
from ro_crate_ingest.settings import get_settings


def pytest_configure(config: pytest.Config):
    set_dev_settings_to_local()


@pytest.fixture(scope="session")
def tmp_bia_data_dir(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("bia_data_dir")
    os.environ["bia_data_dir"] = str(tmp_dir)
    return tmp_dir


@pytest.fixture()
def get_bia_api_client():
    settings = get_settings()
    create_test_user(settings)
    return BIAAPIClient(settings)


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


def get_expected_ro_crate_directory(accession_id: str, source_folder: str) -> dict:
    return Path(__file__).parent / source_folder / "output_data" / accession_id


def get_expected_ro_crate_metadata(accession_id: str, source_folder: str) -> dict:
    expected_ro_crate_metadata_path = (
        get_expected_ro_crate_directory(accession_id, source_folder)
        / "ro-crate-metadata.json"
    )

    with open(expected_ro_crate_metadata_path) as f:
        return json.loads(f.read())


def get_created_ro_crate_metadata(base_path: Path, accession_id: str):
    created_metatadata_path = base_path / accession_id / "ro-crate-metadata.json"

    with open(created_metatadata_path) as f:
        return json.loads(f.read())


def expected_path_to_created_path(
    expected_path: str, output_dir: Path, source_folder: str
) -> Path:
    expected_output_base = Path(__file__).parent / source_folder / "output_data"
    relative = Path(expected_path).relative_to(expected_output_base)
    return output_dir / relative

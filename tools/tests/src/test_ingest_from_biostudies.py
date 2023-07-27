from pathlib import Path
from collections import Counter
import pytest
from unittest import mock
from click.testing import CliRunner
from scripts.ingest_from_biostudies import main
from bia_integrator_core import study
from bia_integrator_core.integrator import load_and_annotate_study

test_accession_id = "S-BIAD000"
test_resources_path = Path(__file__).resolve().parent.parent / f"resources/bia_integrator_data/{test_accession_id}/"

def mocked_requests_get(url):
    """get files requested from ../resources directory"""

    class MockResponse:
        def __init__(self):
            self.status_code = 200
            file_to_get = Path(test_resources_path) / Path(url).name
            try:
                self.content = file_to_get.read_text()
            except Exception:
                raise Exception(f"Could not read {file_to_get}. url={url}")
        def json(self):
            return self.json_data
    return MockResponse()

# Note below that two dummy variables (mock_head and mock_get) are passed
# due to the two mock.patch decorators
@mock.patch("bia_integrator_tools.biostudies.requests.get", side_effect=mocked_requests_get)
@mock.patch("bia_integrator_tools.biostudies.requests.head", side_effect=mocked_requests_get)
def test_ingest_basic_study_from_biostuides(mock_head, mock_get, monkeypatch, tmp_path_factory):
    data_dirpath = tmp_path_factory.mktemp(".bia-integrator-data")
    monkeypatch.setattr(study.settings, "data_dirpath", data_dirpath)
    runner = CliRunner()
    result = runner.invoke(main, [test_accession_id,])

    # Did script run without errors?
    assert result.exit_code == 0

    # Was file saved in expected location
    assert (data_dirpath / "studies" / f"{test_accession_id}.json").is_file()

    # Were correct number of filerefs created?
    # 1 - zipped zarr
    # 2 - normal files
    # 3 - zip archives
    # 4 - zip directories
    expected_fileref_types = {
        "zipped_zarr": 1,
        None: 2,
        "zipped_archive": 3,
        "zipped_directory": 4,
    }
    test_study = load_and_annotate_study(test_accession_id)
    assert len(test_study.file_references) == 10
    
    fileref_types = [
        file_reference.type 
        for file_reference in test_study.file_references.values()
    ]
    actual_fileref_types = dict(Counter(fileref_types))
    assert actual_fileref_types == expected_fileref_types
    

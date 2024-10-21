import pytest
from bia_ingest.cli_logging import ImageCreationResult

# @pytest.fixture
# def test_file_reference() -> List[bia_data_model.FileReference]:
#    """ Return test file reference.
#
#        Return file references with details obtained from filelist in
#        bia-ingest/test/data/file_list_study_component_1.json
#    """


@pytest.fixture
def image_creation_result_summary():
    return ImageCreationResult()

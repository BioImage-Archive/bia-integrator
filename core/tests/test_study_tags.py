import pytest

from . import TEST_SAMPLE_DATA

@pytest.fixture(scope="session")
def disk_backend_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("config")


def test_tags_functional(disk_backend_dir):

    from bia_integrator_core.config import settings

    settings.data_dirpath = disk_backend_dir

    accession_id = "S-BIAD144"
 
    from bia_integrator_core.interface import get_study_tags
    tags = get_study_tags(accession_id)
    assert "2D" not in tags

    from bia_integrator_core.interface import persist_study_tag
    from bia_integrator_core.models import StudyTag
    tag = StudyTag(
        accession_id=accession_id,
        value="2D"
    )
    persist_study_tag(tag)

    tags = get_study_tags(accession_id)
    assert "2D" in tags


def test_tag_annotation(disk_backend_dir):

    from bia_integrator_core.config import settings

    settings.data_dirpath = disk_backend_dir

    accession_id = "S-BIAD144"

    
 
    # from bia_integrator_core.interface import get_study_tags
    # tags = get_study_tags(accession_id)
    # assert "2D" not in tags

    # from bia_integrator_core.interface import persist_study_tag
    # from bia_integrator_core.models import StudyTag
    # tag = StudyTag(
    #     accession_id=accession_id,
    #     value="2D"
    # )
    # persist_study_tag(tag)

    # tags = get_study_tags(accession_id)
    # assert "2D" in tags
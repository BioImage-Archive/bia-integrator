import pytest


@pytest.mark.skip(reason="API changed in 09/24 so tests need revising")
def test_load_study(accession_id, expected_release_date):
    from bia_integrator_core.study import get_study

    bia_study = get_study(accession_id)

    assert bia_study.accession_id == accession_id
    assert bia_study.release_date == expected_release_date

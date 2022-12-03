from . import TEST_SAMPLE_DATA


def test_load_study():

    from bia_integrator_core.study import get_study

    accession_id = "S-BIAD144"

    bia_study = get_study(accession_id)

    assert bia_study.accession_id == accession_id
    assert bia_study.release_date == "2021-05-31"
import pytest


@pytest.mark.skip(reason="API changed in 09/24 so tests need revising")
def test_load_and_annotate(accession_id, expected_example_image_uri):
    from bia_integrator_core.integrator import load_and_annotate_study

    bia_study = load_and_annotate_study(accession_id)

    assert bia_study.accession_id == accession_id
    assert bia_study.example_image_uri == expected_example_image_uri

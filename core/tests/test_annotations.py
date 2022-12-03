from . import TEST_SAMPLE_DATA


def test_get_study_annotations():

    from bia_integrator_core.annotation import get_study_annotations

    accession_id = "S-BIAD144"

    annotations = get_study_annotations(accession_id)

    assert len(annotations) == 1
    assert annotations[0].accession_id == "S-BIAD144"
    assert annotations[0].key == "example_image_uri"
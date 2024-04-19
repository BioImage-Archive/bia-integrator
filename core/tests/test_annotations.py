def test_get_study_annotations(accession_id, expected_annotation_key):

    from bia_integrator_core.annotation import get_study_annotations

    annotations = get_study_annotations(accession_id)

    # Simply test that there is an annotation called example_image_uri
    assert len(annotations) > 0
    annotation_keys = [annotation.key for annotation in annotations]
    assert expected_annotation_key in annotation_keys

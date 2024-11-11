import pytest
from .mock_objects import (
    mock_study,
    mock_biosample,
    mock_dataset,
    mock_specimen_imaging_preparation_protocol,
    mock_image_acquisition_protocol,
    mock_specimen,
    mock_annotation_method,
    mock_specimen_growth_protocol,
)
from bia_ingest.ingest import (
    biosample,
    dataset,
    specimen_imaging_preparation_protocol,
    study,
    image_acquisition_protocol,
    annotation_method,
    specimen,
    specimen_growth_protocol,
)


@pytest.mark.parametrize(
    (
        "expected_model_func",
        "model_creation_func",
    ),
    (
        (
            mock_study.get_affiliation,
            study.get_affiliation,
        ),
        (
            mock_study.get_contributor,
            study.get_contributor,
        ),
        (
            mock_study.get_grant,
            study.get_grant,
        ),
        (
            mock_study.get_study,
            study.get_study,
        ),
        (
            mock_biosample.get_biosample,
            biosample.get_biosample,
        ),
        (
            mock_dataset.get_dataset,
            dataset.get_dataset,
        ),
        (
            mock_specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol,
            specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol,
        ),
        (
            mock_image_acquisition_protocol.get_image_acquisition_protocol,
            image_acquisition_protocol.get_image_acquisition_protocol,
        ),
        (
            mock_specimen.get_specimen,
            specimen.get_specimen,
        ),
        (
            mock_annotation_method.get_annotation_method,
            annotation_method.get_annotation_method,
        ),
        (
            mock_specimen_growth_protocol.get_specimen_growth_protocol,
            specimen_growth_protocol.get_specimen_growth_protocol,
        ),
        #    (
        #    # Not testing as we need to deal with links that are not proper
        #    # urls
        #    # (utils.get_test_external_reference, conversion.get_external_reference,),
        #    # Do not test semantic_models.Publication yet. Need to resolve
        #    # issues around some fields being mandatory or optional
        #    # (utils.get_test_publication, conversion.get_publication,),
        #    # (bia_data_model.Study, conversion.get_study_from_submission,),
    ),
)
def test_create_models(
    expected_model_func,
    model_creation_func,
    test_submission,
    ingestion_result_summary,
    mock_request_get,
):
    expected = expected_model_func()
    created = model_creation_func(test_submission, ingestion_result_summary)
    assert expected == created

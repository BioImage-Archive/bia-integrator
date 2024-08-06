import pytest
from . import utils
from bia_ingest_sm.conversion import (
    biosample,
    experimental_imaging_dataset,
    specimen_imaging_preparation_protocol,
    study,
    specimen_growth_protocol,
    image_acquisition,
    annotation_method,
)


@pytest.mark.parametrize(
    ("expected_model_func", "model_creation_func",),
    (
        (utils.get_test_affiliation, study.get_affiliation,),
        (utils.get_test_contributor, study.get_contributor,),
        (utils.get_test_grant, study.get_grant,),
        (utils.get_test_study, study.get_study,),
        (utils.get_test_biosample, biosample.get_biosample,),
        (
            utils.get_test_experimental_imaging_dataset,
            experimental_imaging_dataset.get_experimental_imaging_dataset,
        ),
        (
            utils.get_test_specimen_imaging_preparation_protocol,
            specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol,
        ),
        (
            utils.get_test_specimen_growth_protocol,
            specimen_growth_protocol.get_specimen_growth_protocol,
        ),
        (utils.get_test_image_acquisition, image_acquisition.get_image_acquisition,),
        (utils.get_test_annotation_method, annotation_method.get_annotation_method,),
        # Not testing as we need to deal with links that are not proper
        # urls
        # (utils.get_test_external_reference, conversion.get_external_reference,),
        # Do not test semantic_models.Publication yet. Need to resolve
        # issues around some fields being mandatory or optional
        # (utils.get_test_publication, conversion.get_publication,),
        # (bia_data_model.Study, conversion.get_study_from_submission,),
    ),
)
def test_create_models(expected_model_func, model_creation_func, test_submission):
    expected = expected_model_func()
    created = model_creation_func(test_submission)
    assert expected == created

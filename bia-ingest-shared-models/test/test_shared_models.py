from typing import Dict
import pytest
from . import utils
from .utils import bia_data_model, semantic_models
from bia_ingest_sm import conversion


@pytest.mark.parametrize(
    ("expected_model_func", "model_creation_func",),
    (
        (utils.get_test_affiliation, conversion.get_affiliation,),
        (utils.get_test_contributor, conversion.get_contributor,),
        (utils.get_test_grant, conversion.get_grant,),
        (utils.get_test_study, conversion.get_study,),
        (utils.get_test_biosample, conversion.get_biosample,),
        (utils.get_test_experimental_imaging_dataset, conversion.get_experimental_imaging_dataset,),
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

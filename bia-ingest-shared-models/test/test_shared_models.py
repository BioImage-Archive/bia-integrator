from typing import Dict, List
from pathlib import Path
from unittest.mock import Mock
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
    file_reference,
)
from bia_ingest_sm.biostudies import requests, File
from pydantic import TypeAdapter

# TODO: Mock requests.get correctly!!!
def mock_request_get(flist_url: str) -> Dict[str, str]:
    data_dir = Path(__file__).parent / "data"
    path_to_load = data_dir / Path(flist_url).name
    return_value = Mock()
    return_value.status_code = 200
    return_value.content = path_to_load.read_text()
    return return_value


requests.get = mock_request_get


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
        (
            utils.get_test_image_acquisition,
            image_acquisition.get_image_acquisition,
        ),
         (
            utils.get_test_annotation_method,
            annotation_method.get_annotation_method,
        ),
        # Test FileReference creation separately as it now has a
        # different pattern of creation from other artefacts i.e.
        # it now needs a submitted dataset
        #(
        #    utils.get_test_file_reference,
        #    file_reference.get_file_reference_by_study_component,
        #),
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


# def test_save_study_artefacts(test_submission):
#    conversion.get_study(test_submission, persist_artefacts=True)

def test_create_file_reference(test_submission):
    file_reference_data = [
        {
            "accession_id": "S-BIADTEST",
            "path": "study_component2/im06.png",
            "type": "file",
            "size": 3,
            "uri": "",
            "attribute": {},
        },
        {
            "accession_id": "S-BIADTEST",
            "path": "study_component2/im08.png",
            "type": "file",
            "size": 123,
            "uri": "",
            "attribute": {},
        },
        {
            "accession_id": "S-BIADTEST",
            "path": "study_component2/ann01-05",
            "type": "file",
            "size": 11,
            "uri": "",
            "attribute": {},
        },
    ]
    files_in_filelist = [File.model_validate(f) for f in file_reference_data]

    expected = utils.get_test_file_reference()
    #created = file_reference.get_file_reference_for_submission_dataset(accession_id="S-BIADTEST", submission_dataset=utils.get_test_experimental_imaging_dataset()[1], files_in_file_list=files_in_filelist)
    datasets_in_submission = [utils.get_test_experimental_imaging_dataset()[1],]
    created = file_reference.get_file_reference_by_study_component(test_submission, datasets_in_submission=datasets_in_submission)
    assert created[datasets_in_submission[0].title_id] == expected

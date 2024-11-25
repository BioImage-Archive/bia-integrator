import pytest
from .mock_objects import (
    mock_study,
    mock_biosample,
    mock_dataset,
    mock_specimen_imaging_preparation_protocol,
    mock_image_acquisition_protocol,
    mock_annotation_method,
    mock_specimen_growth_protocol,
)

from bia_ingest.biostudies.v4 import (
    bio_sample,
    dataset,
    growth_protocol,
    image_acquisition_protocol,
    annotation_method,
    specimen_imaging_preparation_protocol,
    study,
)


def test_create_models_specimen_imaging_preparation_protocol(
    test_submission,
    ingestion_result_summary,
):
    expected = (
        mock_specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol_as_map()
    )
    created = specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol_as_map(
        test_submission, ingestion_result_summary
    )
    assert expected == created


def test_create_models_annotation_method(
    test_submission,
    ingestion_result_summary,
):
    expected = mock_annotation_method.get_annotation_method_as_map()
    created = annotation_method.get_annotation_method_as_map(
        test_submission, ingestion_result_summary
    )
    assert expected == created


def test_create_models_image_acquisition_protocol(
    test_submission,
    ingestion_result_summary,
):
    expected = mock_image_acquisition_protocol.get_image_acquisition_protocol_as_map()
    created = image_acquisition_protocol.get_image_acquisition_protocol_map(
        test_submission, ingestion_result_summary
    )
    assert expected == created


def test_create_models_growth_protocol(
    test_submission,
    ingestion_result_summary,
):
    expected = mock_specimen_growth_protocol.get_growth_protocol_as_map()
    created = growth_protocol.get_growth_protocol_as_map(
        test_submission, ingestion_result_summary
    )
    assert expected == created


@pytest.fixture
def growth_protocol_map():
    return mock_specimen_growth_protocol.get_growth_protocol_as_map()


def test_create_models_biosample(
    growth_protocol_map,
    test_submission,
    ingestion_result_summary,
):
    expected = mock_biosample.get_biosample_as_map()
    created = bio_sample.get_bio_sample_as_map(
        test_submission,
        growth_protocol_map,
        ingestion_result_summary,
    )
    assert expected == created


@pytest.fixture
def association_dict():
    association_object_dict = {}
    association_object_dict |= (
        mock_image_acquisition_protocol.get_image_acquisition_protocol_as_map()
    )
    association_object_dict |= mock_annotation_method.get_annotation_method_as_map()
    association_object_dict |= (
        mock_specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol_as_map()
    )
    association_object_dict |= (
        mock_specimen_growth_protocol.get_growth_protocol_as_map()
    )
    association_object_dict |= mock_biosample.get_biosample_as_map()
    return association_object_dict


def test_create_models_dataset(
    association_dict,
    test_submission,
    ingestion_result_summary,
):
    expected = mock_dataset.get_dataset()
    created = dataset.get_dataset_dict_from_study_component(
        test_submission,
        association_dict,
        ingestion_result_summary,
    )
    assert expected == created


def test_create_models_study(test_submission, ingestion_result_summary):
    expected = mock_study.get_study()
    created = study.get_study(
        test_submission,
        association_dict,
        ingestion_result_summary,
    )
    assert expected == created

from uuid import uuid4
import pytest
from pydantic import ValidationError
from . import utils
from bia_shared_datamodels import bia_data_model


@pytest.mark.parametrize(
    (
        "expected_model_type",
        "model_creation_func",
    ),
    (
        (
            bia_data_model.FileReference,
            utils.get_template_file_reference,
        ),
        (
            bia_data_model.ImageRepresentation,
            utils.get_template_image_representation,
        ),
        (
            bia_data_model.ExperimentalImagingDataset,
            utils.get_template_experimental_imaging_dataset,
        ),
        (
            bia_data_model.Specimen,
            utils.get_template_specimen,
        ),
        (
            bia_data_model.ExperimentallyCapturedImage,
            utils.get_template_experimentally_captured_image,
        ),
        (
            bia_data_model.ImageAcquisition,
            utils.get_template_image_acquisition,
        ),
        (
            bia_data_model.SpecimenImagingPrepartionProtocol,
            utils.get_template_specimen_imaging_preparation_protocol,
        ),
        (
            bia_data_model.BioSample,
            utils.get_template_biosample,
        ),
        (
            bia_data_model.ImageAnnotationDataset,
            utils.get_template_image_annotation_dataset,
        ),
        (
            bia_data_model.AnnotationFileReference,
            utils.get_template_annotation_file_reference,
        ),
        (
            bia_data_model.DerivedImage,
            utils.get_template_derived_image,
        ),
        (
            bia_data_model.AnnotationMethod,
            utils.get_template_annotation_method,
        ),
        (
            bia_data_model.SpecimenGrowthProtocol,
            utils.get_template_specimen_growth_protocol,
        ),
    ),
)
def test_create_models(expected_model_type, model_creation_func):
    expected_model = model_creation_func()
    assert type(expected_model) is expected_model_type


def test_create_study():

    complete_dict = utils.get_study_dict(utils.Completeness.COMPLETE)
    study_complete = bia_data_model.Study(**complete_dict)

    # Check that the model is created
    assert type(study_complete) is bia_data_model.Study
    # Check that the dictionary is indeed "Complete" - no optional fields missed
    assert study_complete.model_dump() == complete_dict
    # Check that there are no inconsistencies in the model definition
    assert (
        type(bia_data_model.Study(**study_complete.model_dump()))
        is bia_data_model.Study
    )

    mimimal_dict = utils.get_study_dict(utils.Completeness.MINIMAL)
    study_minimal = bia_data_model.Study(**mimimal_dict)

    # Check that the model is created
    assert type(study_minimal) is bia_data_model.Study
    # Check that the dictionary is indeed "Minimal" - no optional fields included
    for key in mimimal_dict:
        less_than_minimal_dict = mimimal_dict.copy()
        del less_than_minimal_dict[key]
        with pytest.raises(ValidationError):
            bia_data_model.Study(**less_than_minimal_dict)
    # Check that there are no inconsistencies in the model definition's optional fields
    assert (
        type(bia_data_model.Study(**study_minimal.model_dump())) is bia_data_model.Study
    )


def test_create_specimen_with_empty_lists_fails():
    with pytest.raises(ValidationError):
        specimen = bia_data_model.Specimen.model_validate(
            {
                "sample_of": [],
                "preparation_method": [],
            }
        )
        specimen = bia_data_model.Specimen.model_validate(
            {
                "sample_of": [uuid4()],
                "preparation_method": [],
            }
        )
        specimen = bia_data_model.Specimen.model_validate(
            {
                "sample_of": [],
                "preparation_method": [uuid4()],
            }
        )

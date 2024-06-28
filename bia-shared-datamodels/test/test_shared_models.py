from uuid import uuid4
import pytest
from pydantic import ValidationError
from . import utils
from .utils import (
    bia_data_model,
    semantic_models,
)


@pytest.mark.parametrize(
    ("expected_model_type", "model_creation_func",),
    (
        (bia_data_model.Study, utils.get_template_study,),
        (bia_data_model.FileReference, utils.get_template_file_reference,),
        (bia_data_model.ImageRepresentation, utils.get_template_image_representation,),
        (
            bia_data_model.ExperimentalImagingDataset,
            utils.get_template_experimental_imaging_dataset,
        ),
        (bia_data_model.Specimen, utils.get_template_specimen,),
        (
            bia_data_model.ExperimentallyCapturedImage,
            utils.get_template_experimentally_captured_image,
        ),
        (bia_data_model.ImageAcquisition, utils.get_template_image_acquisition,),
        (
            bia_data_model.SpecimenPrepartionProtocol,
            utils.get_template_specimen_preparation_protocol,
        ),
        (bia_data_model.BioSample, utils.get_template_biosample,),
        (
            bia_data_model.ImageAnnotationDataset,
            utils.get_template_image_annotation_dataset,
        ),
        (
            bia_data_model.AnnotationFileReference,
            utils.get_template_annotation_file_reference,
        ),
        (bia_data_model.DerivedImage, utils.get_template_derived_image,),
        (bia_data_model.AnnotationMethod, utils.get_template_annotation_method,),
    ),
)
def test_create_models(expected_model_type, model_creation_func):
    expected_model = model_creation_func()
    assert type(expected_model) is expected_model_type


def test_create_specimen_with_empty_lists_fails():
    with pytest.raises(ValidationError):
        specimen = bia_data_model.Specimen.model_validate(
            {"sample_of": [], "preparation_method": [],}
        )
        specimen = bia_data_model.Specimen.model_validate(
            {"sample_of": [uuid4()], "preparation_method": [],}
        )
        specimen = bia_data_model.Specimen.model_validate(
            {"sample_of": [], "preparation_method": [uuid4()],}
        )

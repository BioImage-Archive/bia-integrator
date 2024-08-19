import pytest
from pydantic import ValidationError, BaseModel
from bia_shared_datamodels import bia_data_model, semantic_models, mock_objects
from typing import Callable

@pytest.mark.parametrize(
    ("expected_model_type", "dict_creation_func"),
    (
        (semantic_models.Taxon, mock_objects.get_taxon_dict),
        (semantic_models.Channel, mock_objects.get_channel_dict),
        (semantic_models.RenderedView, mock_objects.get_rendered_view_dict),
        (
            semantic_models.SignalChannelInformation,
            mock_objects.get_signal_channel_information_dict,
        ),
        (
            bia_data_model.SpecimenImagingPreparationProtocol,
            mock_objects.get_specimen_imaging_preparation_protocol_dict,
        ),
        (
            bia_data_model.SpecimenGrowthProtocol,
            mock_objects.get_specimen_growth_protocol_dict,
        ),
        (bia_data_model.BioSample, mock_objects.get_biosample_dict),
        (bia_data_model.Specimen, mock_objects.get_specimen_dict),
        (bia_data_model.AnnotationMethod, mock_objects.get_annotation_method_dict),
        (
            bia_data_model.ExperimentallyCapturedImage,
            mock_objects.get_experimentally_captured_image_dict,
        ),
        (bia_data_model.DerivedImage, mock_objects.get_derived_image_dict),
        (
            bia_data_model.ImageAnnotationDataset,
            mock_objects.get_image_annotation_dataset_dict,
        ),
        (bia_data_model.ImageAcquisition, mock_objects.get_image_acquisition_dict),
        (semantic_models.ImageAnalysisMethod, mock_objects.get_image_analysis_method_dict),
        (
            semantic_models.ImageCorrelationMethod,
            mock_objects.get_image_correlation_method_dict,
        ),
        (
            bia_data_model.ExperimentalImagingDataset,
            mock_objects.get_experimental_imaging_dataset_dict,
        ),
        (
            bia_data_model.AnnotationFileReference,
            mock_objects.get_annotation_file_reference_dict,
        ),
        (bia_data_model.FileReference, mock_objects.get_file_reference_dict),
        (bia_data_model.ImageRepresentation, mock_objects.get_image_representation_dict),
        (semantic_models.Affiliation, mock_objects.get_affiliation_dict),
        (semantic_models.Contributor, mock_objects.get_contributor_dict),
        (bia_data_model.Study, mock_objects.get_study_dict),
    ),
)
class TestCreateObject:
    def test_create_complete_object(
        self,
        expected_model_type: BaseModel,
        dict_creation_func: Callable[[mock_objects.Completeness], dict],
    ):
        complete_dict = dict_creation_func(mock_objects.Completeness.COMPLETE)
        complete_model: BaseModel = expected_model_type(**complete_dict)

        # Check that the model is created
        assert type(complete_model) is expected_model_type
        # Check that the dictionary is indeed "Complete" - no optional fields missed
        assert complete_model.model_dump() == complete_dict
        # Check that there are no inconsistencies in the model definition
        assert (
            type(expected_model_type(**complete_model.model_dump()))
            is expected_model_type
        )


    def test_create_minimal_object(
        self,
        expected_model_type: BaseModel,
        dict_creation_func: Callable[[mock_objects.Completeness], dict],
    ):
        mimimal_dict = dict_creation_func(mock_objects.Completeness.MINIMAL)
        minimal_model: BaseModel = expected_model_type(**mimimal_dict)

        # Check that the model is created
        assert type(minimal_model) is expected_model_type
        # Check that the dictionary is indeed "Minimal" - no optional fields included, and list fields are of minimum length
        for key in mimimal_dict:
            less_than_minimal_dict = mimimal_dict.copy()
            if (
                isinstance(less_than_minimal_dict[key], list)
                and len(less_than_minimal_dict[key]) > 0
            ):
                less_than_minimal_dict[key] = []
                with pytest.raises(ValidationError):
                    expected_model_type(**less_than_minimal_dict)

            del less_than_minimal_dict[key]
            with pytest.raises(ValidationError):
                expected_model_type(**less_than_minimal_dict)
        # Check that there are no inconsistencies in the model definition's optional fields
        assert (
            type(expected_model_type(**minimal_model.model_dump()))
            is expected_model_type
        )

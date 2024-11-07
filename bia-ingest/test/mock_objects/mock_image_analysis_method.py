from bia_shared_datamodels import semantic_models


def get_image_analysis_method() -> semantic_models.ImageAnalysisMethod:
    return semantic_models.ImageAnalysisMethod.model_validate(
        {
            "protocol_description": "Test image analysis",
            "features_analysed": "Test image analysis overview",
        }
    )

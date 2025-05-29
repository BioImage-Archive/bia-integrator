from bia_shared_datamodels import semantic_models


def get_image_analysis_method() -> semantic_models.ImageAnalysisMethod:
    return semantic_models.ImageAnalysisMethod.model_validate(
        {
            "title": "Test image analysis",
            "protocol_description": "Test image analysis overview",
            # "features_analysed": "",
        }
    )


def get_image_analysis_method_as_map() -> (
    dict[str, semantic_models.ImageAnalysisMethod]
):
    return {"Test image analysis": get_image_analysis_method()}

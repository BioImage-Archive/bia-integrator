from bia_shared_datamodels import semantic_models


def get_image_analysis_method() -> semantic_models.ImageAnalysisMethod:
    return semantic_models.ImageAnalysisMethod.model_validate(
        {
            "protocol_description": "Test image analysis",
            # TODO: clarify with FS/pagetab where title comes from.
            "title": "Test image analysis",
            "features_analysed": "Test image analysis overview",
        }
    )


def get_image_analysis_method_as_map() -> (
    dict[str, semantic_models.ImageAnalysisMethod]
):
    return {"Test image analysis": get_image_analysis_method()}

from bia_shared_datamodels import semantic_models


def get_test_image_correlation_method() -> semantic_models.ImageCorrelationMethod:
    return semantic_models.ImageCorrelationMethod.model_validate(
        {
            "protocol_description": "Template Analysis method",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    )


def get_test_image_correlation_method_as_map() -> (
    dict[str, semantic_models.ImageCorrelationMethod]
):
    return {"Test image correlation": get_test_image_correlation_method()}

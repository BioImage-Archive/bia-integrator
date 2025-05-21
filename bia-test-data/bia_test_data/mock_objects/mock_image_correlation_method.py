from bia_shared_datamodels import semantic_models


def get_image_correlation_method() -> semantic_models.ImageCorrelationMethod:
    return semantic_models.ImageCorrelationMethod.model_validate(
        {
            "title": "Template correlation method",
            # TODO: confirm with FS where this comes from. Spatial and temporal alignment?
            "protocol_description": "Template correlation method description",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    )


def get_image_correlation_method_as_map() -> (
    dict[str, semantic_models.ImageCorrelationMethod]
):
    return {"Template correlation method": get_image_correlation_method()}

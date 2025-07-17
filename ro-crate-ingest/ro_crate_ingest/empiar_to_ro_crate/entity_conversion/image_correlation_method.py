import logging
from bia_shared_datamodels.ro_crate_models import ImageCorrelationMethod

logger = logging.getLogger("__main__." + __name__)


def get_image_correlation_methods(
    rembi_yaml: dict,
) -> dict[str, ImageCorrelationMethod]:

    yaml_list_of_objs = rembi_yaml.get("dataset_rembis", {}).get(
        "ImageCorrelationMethod", []
    )

    roc_objects = []
    for yaml_object in yaml_list_of_objs:

        roc_objects.append(get_image_correlation_method(yaml_object))

    return roc_objects


def get_image_correlation_method(yaml_object: dict) -> ImageCorrelationMethod:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:ImageAnalysisMethod"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "fiducialsUsed": yaml_object.get("fiducials_used", None),
        "transformationMatrix": yaml_object.get("transformation_matrix", None),
    }

    return ImageCorrelationMethod(**model_dict)

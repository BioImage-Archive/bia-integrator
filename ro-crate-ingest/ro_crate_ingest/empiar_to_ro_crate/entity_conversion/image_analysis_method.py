import logging
from bia_shared_datamodels.ro_crate_models import ImageAnalysisMethod

logger = logging.getLogger("__main__." + __name__)


def get_image_analysis_methods(
    rembi_yaml: dict,
) -> list[ImageAnalysisMethod]:

    yaml_list_of_objs = rembi_yaml.get("dataset_rembis", {}).get(
        "ImageAnalysisMethod", []
    )

    roc_objects = []
    for yaml_object in yaml_list_of_objs:
        roc_objects.append(get_image_analysis_method(yaml_object))

    return roc_objects


def get_image_analysis_method(yaml_object: dict) -> ImageAnalysisMethod:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:ImageAnalysisMethod"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "featuresAnalysed": yaml_object["features_analysed"],
    }

    return ImageAnalysisMethod(**model_dict)

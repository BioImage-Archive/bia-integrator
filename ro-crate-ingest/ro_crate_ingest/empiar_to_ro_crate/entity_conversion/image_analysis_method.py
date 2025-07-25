import logging
from bia_shared_datamodels import ro_crate_models

logger = logging.getLogger("__main__." + __name__)


def get_image_analysis_methods_by_title(
    rembi_yaml: dict,
) -> dict[str, ro_crate_models.ImageAnalysisMethod]:

    yaml_list_of_objs = rembi_yaml.get("dataset_rembis", {}).get(
        "ImageAnalysisMethod", []
    )

    roc_objects_dict = {}
    for yaml_object in yaml_list_of_objs:
        roc_object = get_image_analysis_method(yaml_object)
        roc_objects_dict[roc_object.title] = roc_object

    return roc_objects_dict


def get_image_analysis_method(yaml_object: dict) -> ro_crate_models.ImageAnalysisMethod:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:ImageAnalysisMethod"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "featuresAnalysed": yaml_object["features_analysed"],
    }

    return ro_crate_models.ImageAnalysisMethod(**model_dict)

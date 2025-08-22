import logging
from bia_shared_datamodels.ro_crate_models import ImageCorrelationMethod

logger = logging.getLogger("__main__." + __name__)


def get_image_correlation_methods_by_title(
    rembi_yaml: dict,
) -> dict[str, ImageCorrelationMethod]:

    yaml_list_of_objs = rembi_yaml.get("dataset_rembis", {}).get(
        "ImageCorrelationMethod", []
    )

    roc_objects_dict = {}
    for yaml_object in yaml_list_of_objs:
        roc_object = get_image_correlation_method(yaml_object)
        roc_objects_dict[roc_object.title] = roc_object

    return roc_objects_dict


def get_image_correlation_method(yaml_object: dict) -> ImageCorrelationMethod:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:ImageCorrelationMethod"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "fiducialsUsed": yaml_object.get("fiducials_used", None),
        "transformationMatrix": yaml_object.get("transformation_matrix", None),
    }

    return ImageCorrelationMethod(**model_dict)

from bia_shared_datamodels.ro_crate_models import AnnotationMethod
import logging

logger = logging.getLogger("__main__." + __name__)


def get_annotation_methods(
    rembi_yaml: dict,
) -> list[AnnotationMethod]:
    yaml_list_of_objs = rembi_yaml.get("rembis", {}).get("AnnotationMethod", [])

    roc_objects = []
    for yaml_object in yaml_list_of_objs:

        roc_objects.append(get_annotation_method(yaml_object))

    return roc_objects


def get_annotation_method(
    yaml_object: dict,
) -> AnnotationMethod:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:AnnotationMethod"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "methodType": yaml_object.get("method_type", []),
    }

    return AnnotationMethod(**model_dict)

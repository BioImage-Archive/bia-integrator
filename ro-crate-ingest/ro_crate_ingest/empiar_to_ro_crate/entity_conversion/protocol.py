import logging
from bia_shared_datamodels import ro_crate_models

logger = logging.getLogger("__main__." + __name__)


def get_protocols(
    rembi_yaml: dict,
) -> list[ro_crate_models.Protocol]:
    yaml_list_of_objs = rembi_yaml.get("rembis", {}).get("Protocol", [])

    roc_objects = []
    for yaml_object in yaml_list_of_objs:

        roc_objects.append(get_protocol(yaml_object))

    return roc_objects


def get_protocol(yaml_object: dict) -> ro_crate_models.Protocol:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:Protocol"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
    }

    return ro_crate_models.Protocol(**model_dict)

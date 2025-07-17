from bia_shared_datamodels.ro_crate_models import ImageAcquisitionProtocol
import logging

logger = logging.getLogger("__main__." + __name__)


def get_image_acquisition_protocols(rembi_yaml: dict) -> list[ImageAcquisitionProtocol]:
    yaml_list_of_objs = rembi_yaml.get("rembis", {}).get("ImageAcquisitionProtocol", [])

    roc_objects = []
    for yaml_object in yaml_list_of_objs:

        roc_objects.append(get_image_acquisition_protocol(yaml_object))

    return roc_objects


def get_image_acquisition_protocol(yaml_object: dict) -> ImageAcquisitionProtocol:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:ImageAcquisitionProtocol"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "imagingInstrumentDescription": yaml_object.get(
            "imaging_instrument_description", ""
        ),
        "imagingMethodName": yaml_object.get("imaging_method_name", []),
        "fbbiId": yaml_object.get("fbbi_id", []),
    }

    return ImageAcquisitionProtocol(**model_dict)

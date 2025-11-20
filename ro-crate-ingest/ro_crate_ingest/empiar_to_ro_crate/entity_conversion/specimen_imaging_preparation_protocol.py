from bia_shared_datamodels.ro_crate_models import SpecimenImagingPreparationProtocol
import logging

logger = logging.getLogger("__main__." + __name__)


def get_specimen_imaging_preparation_protocols(
    rembi_yaml: dict,
) -> list[SpecimenImagingPreparationProtocol]:
    yaml_list_of_objs = rembi_yaml["rembis"]["SpecimenImagingPreparationProtocol"]

    roc_objects = []
    for yaml_object in yaml_list_of_objs:
        roc_objects.append(get_specimen_imaging_preparation_protocol(yaml_object))

    return roc_objects


def get_specimen_imaging_preparation_protocol(
    yaml_object: dict,
) -> SpecimenImagingPreparationProtocol:

    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:SpecimenImagingPreparationProtocol"],
        "title": yaml_object["title"],
        "protocolDescription": yaml_object["protocol_description"],
        "signalChannelInformation": [],
    }

    return SpecimenImagingPreparationProtocol(**model_dict)

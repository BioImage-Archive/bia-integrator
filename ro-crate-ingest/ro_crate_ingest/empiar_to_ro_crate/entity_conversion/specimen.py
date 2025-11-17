from bia_shared_datamodels.ro_crate_models import Specimen
import logging

logger = logging.getLogger("__main__." + __name__)


def get_specimens(
    rembi_yaml: dict,
) -> list[Specimen]:

    yaml_list_of_objs = rembi_yaml.get("rembis", {}).get(
        "Specimen", []
    )
    
    roc_objects = []
    for yaml_object in yaml_list_of_objs:
        roc_objects.append(get_specimen(yaml_object))
    
    return roc_objects


def get_specimen(yaml_object: dict) -> Specimen:
    
    biosample_titles = yaml_object.get("biosample_title", [])
    if isinstance(biosample_titles, str):
        biosample_titles = [biosample_titles]
    
    specimen_imaging_prep_protocol_titles = yaml_object.get("specimen_imaging_preparation_protocol_title", [])
    if isinstance(specimen_imaging_prep_protocol_titles, str):
        specimen_imaging_prep_protocol_titles = [specimen_imaging_prep_protocol_titles]
    
    model_dict = {
        "@id": f"_:{yaml_object["title"]}",
        "@type": ["bia:Specimen"],
        "biologicalEntity": [{"@id": f"_:{title}"} for title in biosample_titles],
        "imagingPreparationProtocol": [{"@id": f"_:{title}"} for title in specimen_imaging_prep_protocol_titles],
    }
    
    return Specimen(**model_dict)
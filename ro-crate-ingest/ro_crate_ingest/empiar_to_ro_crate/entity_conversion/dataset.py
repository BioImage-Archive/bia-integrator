from bia_shared_datamodels.ro_crate_models import Dataset
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Imageset, Entry
import logging
from urllib.parse import quote

logger = logging.getLogger("__main__." + __name__)


def get_datasets(yaml_file: dict, empiar_api_entry: Entry) -> list[Dataset]:
    yaml_list_of_objs = yaml_file.get("datasets", [])

    imageset_by_name = {
        imageset.name: imageset for imageset in empiar_api_entry.imagesets
    }

    datasets = []

    for obj_dict in yaml_list_of_objs:
        imageset = imageset_by_name[obj_dict["title"]]
        datasets.append(get_dataset(imageset=imageset, yaml_dict=obj_dict))

    return datasets


def get_dataset(imageset: Imageset, yaml_dict: dict) -> Dataset:

    association_yaml_fields = aggregate_assoications(yaml_dict)

    model_dict = {
        "@id": quote(f"{imageset.name} {imageset.directory}/"),
        "@type": ["Dataset", "bia:Dataset"],
        "title": imageset.name,
        "description": imageset.details,
        "hasPart": [],
        "associatedImageAcquisitionProtocol": association_yaml_fields[
            "image_acquisition_protocol_title"
        ],
        "associatedSpecimenImagingPreparationProtocol": association_yaml_fields[
            "specimen_imaging_preparation_protocol_title"
        ],
        "associatedBiologicalEntity": association_yaml_fields["biosample_title"],
        "associatedAnnotationMethod": association_yaml_fields[
            "annotation_method_title"
        ],
        "associatedProtocol": [],
    }
    return Dataset(**model_dict)


def aggregate_assoications(yaml_dict: dict) -> dict:

    association_yaml_fields = {
        "biosample_title": [],
        "image_acquisition_protocol_title": [],
        "specimen_imaging_preparation_protocol_title": [],
        "annotation_method_title": [],
    }

    for image in yaml_dict.get("assigned_images", []):
        for field in association_yaml_fields:
            if field in image:
                id = {"@id": f"_:{image[field]}"}
                if id not in association_yaml_fields[field]:
                    association_yaml_fields[field].append(id)

    return association_yaml_fields

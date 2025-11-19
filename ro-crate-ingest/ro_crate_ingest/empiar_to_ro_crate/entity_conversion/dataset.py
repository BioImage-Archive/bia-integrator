from bia_shared_datamodels import ro_crate_models
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Imageset, Entry
from ro_crate_ingest.empiar_to_ro_crate.entity_conversion.file_list import (
    generate_relative_filelist_path,
)
import logging
from itertools import chain
from urllib.parse import quote

logger = logging.getLogger("__main__." + __name__)


def get_datasets_by_imageset_title(
    yaml_file: dict,
    empiar_api_entry: Entry,
) -> dict[str, ro_crate_models.Dataset]:

    imageset_by_name = {
        imageset.name: imageset for imageset in empiar_api_entry.imagesets
    }

    yaml_list_of_datasets = yaml_file.get("datasets", [])
    yaml_list_of_specimens = yaml_file.get("rembis", {}).get("Specimen", [])

    datasets = {}
    for dataset_dict in yaml_list_of_datasets:
        imageset = imageset_by_name[dataset_dict["title"]]
        datasets[dataset_dict["title"]] = get_dataset(
            imageset=imageset,
            dataset_dict=dataset_dict,
            specimens_yaml=yaml_list_of_specimens,
        )

    return datasets


def get_dataset(
    imageset: Imageset,
    dataset_dict: dict, 
    specimens_yaml: list[dict], 
) -> ro_crate_models.Dataset:

    association_yaml_fields = {
        "biosample_title": [],
        "image_acquisition_protocol_title": [],
        "specimen_imaging_preparation_protocol_title": [],
        "annotation_method_title": [],
        "protocol_title": [],
        "image_analysis_method_title": [],
        "image_correlation_method_title": [],
    }

    get_assigned_dataset_rembis_and_associations_from_assigned_objects(
        association_yaml_fields, 
        dataset_dict,
    )

    get_associations_via_assigned_specimens(
        association_yaml_fields, 
        dataset_dict, 
        specimens_yaml, 
    )

    id = quote(dataset_dict.get("id", f"{imageset.name} {imageset.directory}/"))

    filelist_id = generate_relative_filelist_path(id)

    model_dict = {
        "@id": id,
        "@type": ["Dataset", "bia:Dataset"],
        "title": imageset.name,
        "description": imageset.details,
        "hasPart": [{"@id": filelist_id}],
        "associatedImageAcquisitionProtocol": association_yaml_fields[
            "image_acquisition_protocol_title"
        ],
        "associatedSpecimenImagingPreparationProtocol": association_yaml_fields[
            "specimen_imaging_preparation_protocol_title"
        ],
        "associatedBiologicalEntity": association_yaml_fields["biosample_title"],
        "associatedAnnotationMethod": association_yaml_fields["annotation_method_title"],
        "associatedImageAnalysisMethod": association_yaml_fields["image_analysis_method_title"],
        "associatedImageCorrelationMethod": association_yaml_fields["image_correlation_method_title"],
        "associatedProtocol": association_yaml_fields["protocol_title"],
        "associationFileMetadata": {"@id": filelist_id},
    }
    return ro_crate_models.Dataset(**model_dict)


def get_assigned_dataset_rembis_and_associations_from_assigned_objects(
        association_yaml_fields: dict,
        dataset_dict: dict, 
) -> dict:
    
    for yaml_object in chain(
        dataset_dict.get("assigned_dataset_rembis", []),
        dataset_dict.get("assigned_images", []), 
        dataset_dict.get("assigned_annotations", [])
    ):
        for field in association_yaml_fields:
            if field in yaml_object:
                titles = [yaml_object[field]] if isinstance(yaml_object[field], str) else yaml_object[field]
                for title in titles:
                    id = {"@id": f"_:{title}"}
                    if id not in association_yaml_fields[field]:
                        association_yaml_fields[field].append(id)

    return association_yaml_fields


def get_associations_via_assigned_specimens(
        association_yaml_fields: dict, 
        dataset_dict: dict, 
        specimens_yaml: list[dict], 
) -> dict:
    
    specimen_titles = [
        yaml_object["specimen_title"] 
        for yaml_object in dataset_dict.get("assigned_images", []) 
        if "specimen_title" in yaml_object
    ]

    for specimen_yaml in specimens_yaml:
        if specimen_yaml["title"] in specimen_titles:
            for field in association_yaml_fields:
                if field in specimen_yaml:
                    titles = [specimen_yaml[field]] if isinstance(specimen_yaml[field], str) else specimen_yaml[field]
                    for title in titles:
                        id = {"@id": f"_:{title}"}
                        if id not in association_yaml_fields[field]:
                            association_yaml_fields[field].append(id)

    return association_yaml_fields

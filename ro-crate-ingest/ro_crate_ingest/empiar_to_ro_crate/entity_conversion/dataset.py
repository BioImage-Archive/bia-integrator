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
    image_analysis_methods_map: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method_map: dict[str, ro_crate_models.ImageCorrelationMethod],
) -> dict[str, ro_crate_models.Dataset]:
    yaml_list_of_objs = yaml_file.get("datasets", [])

    imageset_by_name = {
        imageset.name: imageset for imageset in empiar_api_entry.imagesets
    }

    datasets = {}

    for obj_dict in yaml_list_of_objs:
        imageset = imageset_by_name[obj_dict["title"]]
        datasets[obj_dict["title"]] = get_dataset(
            imageset=imageset,
            yaml_dict=obj_dict,
            image_analysis_methods_map=image_analysis_methods_map,
            image_correlation_method_map=image_correlation_method_map,
        )

    return datasets


def get_dataset(
    imageset: Imageset,
    yaml_dict: dict,
    image_analysis_methods_map: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method_map: dict[str, ro_crate_models.ImageCorrelationMethod],
) -> ro_crate_models.Dataset:

    association_yaml_fields = aggregate_associations(yaml_dict)

    image_analysis_methods, image_correlations = get_assigned_dataset_rembis(
        yaml_dict, image_analysis_methods_map, image_correlation_method_map
    )

    id = quote(yaml_dict.get("id", f"{imageset.name} {imageset.directory}/"))

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
        "associatedImageAnalysisMethod": image_analysis_methods,
        "associatedImageCorrelationMethod": image_correlations,
        "associatedProtocol": [],
        "associationFileMetadata": {"@id": filelist_id},
    }
    return ro_crate_models.Dataset(**model_dict)


def aggregate_associations(yaml_dict: dict) -> dict:

    association_yaml_fields = {
        "biosample_title": [],
        "image_acquisition_protocol_title": [],
        "specimen_imaging_preparation_protocol_title": [],
        "annotation_method_title": [],
    }

    for yaml_object in chain(
        yaml_dict.get("assigned_images", []), 
        yaml_dict.get("assigned_annotations", [])
    ):
        for field in association_yaml_fields:
            if field in yaml_object:
                titles = [yaml_object[field]] if isinstance(yaml_object[field], str) else yaml_object[field]
                for title in titles:
                    id = {"@id": f"_:{title}"}
                    if id not in association_yaml_fields[field]:
                        association_yaml_fields[field].append(id)

    return association_yaml_fields


def get_assigned_dataset_rembis(
    yaml_dict: dict,
    image_analysis_methods_map: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method_map: dict[str, ro_crate_models.ImageCorrelationMethod],
):
    image_analysis_methods = []
    image_correlations = []
    for label_dict in yaml_dict.get("assigned_dataset_rembis", []):
        if label_dict["label"] in image_analysis_methods_map:
            image_analysis_methods.append(
                {"@id": image_analysis_methods_map[label_dict["label"]].id}
            )
        elif label_dict["label"] in image_correlation_method_map:
            image_correlations.append(
                {"@id": image_correlation_method_map[label_dict["label"]].id}
            )
        else:
            logger.warning(
                f"Did not find the reference dataset_rembis object {label_dict["label"]} in {yaml_dict["title"]}"
            )
    return image_analysis_methods, image_correlations

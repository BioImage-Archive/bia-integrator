from bia_shared_datamodels import ro_crate_models
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Imageset, Entry
import logging
from urllib.parse import quote

logger = logging.getLogger("__main__." + __name__)


def get_datasets(
    yaml_file: dict,
    empiar_api_entry: Entry,
    image_analysis_methods_map: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method_map: dict[str, ro_crate_models.ImageCorrelationMethod],
) -> list[ro_crate_models.Dataset]:
    yaml_list_of_objs = yaml_file.get("datasets", [])

    imageset_by_name = {
        imageset.name: imageset for imageset in empiar_api_entry.imagesets
    }

    datasets = []

    for obj_dict in yaml_list_of_objs:
        imageset = imageset_by_name[obj_dict["title"]]
        datasets.append(
            get_dataset(
                imageset=imageset,
                yaml_dict=obj_dict,
                image_analysis_methods_map=image_analysis_methods_map,
                image_correlation_method_map=image_correlation_method_map,
            )
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
        "associatedAnnotationMethod": [
            f"_:{x["annotation_method_title"]}"
            for x in yaml_dict.get("assigned_annotations", [])
        ],
        "associatedImageAnalysisMethod": image_analysis_methods,
        "associatedImageCorrelationMethod": image_correlations,
        "associatedProtocol": [],
    }
    return ro_crate_models.Dataset(**model_dict)


def aggregate_associations(yaml_dict: dict) -> dict:

    association_yaml_fields = {
        "biosample_title": [],
        "image_acquisition_protocol_title": [],
        "specimen_imaging_preparation_protocol_title": [],
    }

    for image in yaml_dict.get("assigned_images", []):
        for field in association_yaml_fields:
            if field in image:
                id = {"@id": f"_:{image[field]}"}
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
    for title in yaml_dict.get("assigned_dataset_rembis", []):
        if title in image_analysis_methods_map:
            image_analysis_methods.append({"@id": image_analysis_methods_map[title].id})
        elif title in image_correlation_method_map:
            image_correlations.append({"@id": image_correlation_method_map[title].id})
        else:
            logger.warning(
                f"Did not find the reference dataset_rembis object {title} in {yaml_dict["title"]}"
            )
    return image_analysis_methods, image_correlations

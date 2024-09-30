from glob import glob
from uuid import UUID
from bia_export.website_export.utils import read_all_json, read_api_json_file
from pathlib import Path
from .models import StudyCLIContext
from bia_shared_datamodels import semantic_models, bia_data_model
from bia_integrator_api import models as api_models
import json
from typing import List, Type
import logging
from bia_export.bia_client import api_client

logger = logging.getLogger("__main__." + __name__)


def retrieve_study(context: StudyCLIContext) -> api_models.Study:
    if context.root_directory:
        study_path = context.root_directory.joinpath(
            f"studies/{context.accession_id}.json"
        )

        logger.info(f"Loading study from {study_path}")

        api_study = read_api_json_file(study_path, api_models.Study)
    else:
        api_study = api_client.get_study(str(context.study_uuid))

    return api_study


def retrieve_experimental_imaging_datasets(
    context: StudyCLIContext,
) -> api_models.ExperimentalImagingDataset:
    if context.root_directory:
        eid_directory = context.root_directory.joinpath(
            f"experimental_imaging_datasets/{context.accession_id}/*.json"
        )

        api_eids: List[api_models.ExperimentalImagingDataset] = read_all_json(
            eid_directory, api_models.ExperimentalImagingDataset
        )
    else:
        api_eids = api_client.get_experimental_imaging_dataset_in_study(
            str(context.study_uuid)
        )

    return api_eids


def retrieve_aggregation_fields(
    dataset: bia_data_model.DocumentMixin, context: StudyCLIContext
):
    if context.root_directory:
        try:
            dataset_aggregation_fields = context.dataset_file_aggregate_data[
                dataset.uuid
            ]
            dataset_aggregation_fields["file_type_aggregation"] = sorted(
                list(dataset_aggregation_fields["file_type_aggregation"])
            )
        except KeyError:
            dataset_aggregation_fields = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": [],
            }
    else:
        if dataset.model.type_name == "ExperimentalImagingDataset":
            images = api_client.get_experimentally_captured_image_in_experimental_imaging_dataset(
                str(dataset.uuid)
            )
            files = api_client.get_file_reference_in_experimental_imaging_dataset(
                str(dataset.uuid)
            )
        elif dataset.model.type_name == "ImageAnnotationDataset":
            images = api_client.get_derived_image_in_image_annotation_dataset(
                str(dataset.uuid)
            )
            files = api_client.get_file_reference_in_image_annotation_dataset(
                str(dataset.uuid)
            )

        file_type_aggregation = set()
        for file_reference in files:
            file_type = Path(file_reference.file_path).suffix
            file_type_aggregation.add(file_type)

        dataset_aggregation_fields = {
            "file_count": len(files),
            "image_count": len(images),
            "file_type_aggregation": sorted(list(file_type_aggregation)),
        }

    return dataset_aggregation_fields


def aggregate_file_list_data(context: StudyCLIContext) -> dict[UUID, dict]:
    dataset_counts_map = {}
    file_reference_directory = context.root_directory.joinpath(
        f"file_references/{context.accession_id}/*.json"
    )
    file_reference_paths = glob(str(file_reference_directory))
    for file_path in file_reference_paths:
        with open(file_path, "r") as object_file:
            object_dict = json.load(object_file)
            file_reference = api_models.FileReference(**object_dict)
        submission_dataset = file_reference.submission_dataset_uuid
        file_type = Path(file_reference.file_path).suffix
        if submission_dataset not in dataset_counts_map:
            dataset_counts_map[submission_dataset] = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": set(),
            }
        dataset_counts_map[submission_dataset]["file_count"] += 1
        dataset_counts_map[submission_dataset]["file_type_aggregation"].add(file_type)

    experimentally_derived_images_directory = context.root_directory.joinpath(
        f"experimentally_captured_images/{context.accession_id}/*.json"
    )
    derived_images_directory = context.root_directory.joinpath(
        f"derived_images/{context.accession_id}/*.json"
    )
    image_paths = glob(str(experimentally_derived_images_directory)) + glob(
        str(derived_images_directory)
    )
    for image_path in image_paths:
        with open(image_path, "r") as object_file:
            object_dict = json.load(object_file)
        submission_dataset = object_dict["submission_dataset_uuid"]
        file_type = Path(file_reference.file_path).suffix
        if submission_dataset not in dataset_counts_map:
            dataset_counts_map[submission_dataset] = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": set(),
            }
        dataset_counts_map[submission_dataset]["image_count"] += 1

    return dataset_counts_map


def retrieve_dataset_images(
    dataset_uuid: UUID,
    image_type: Type[semantic_models.AbstractImageMixin],
    context: StudyCLIContext,
) -> List[api_models.ExperimentallyCapturedImage]:
    if context.root_directory:

        directory_map = {
            api_models.ExperimentallyCapturedImage: "experimentally_captured_images",
            api_models.DerivedImage: "derived_images",
        }

        image_directory = context.root_directory.joinpath(
            f"{directory_map[image_type]}/{context.accession_id}/*.json"
        )
        all_api_images: List[semantic_models.AbstractImageMixin] = read_all_json(
            image_directory, image_type
        )
        api_images = [
            image
            for image in all_api_images
            if image.submission_dataset_uuid == dataset_uuid
        ]

    else:
        if image_type == api_models.ExperimentallyCapturedImage:
            api_images = api_client.get_experimentally_captured_image_in_experimental_imaging_dataset(
                str(dataset_uuid)
            )
        elif image_type == api_models.DerivedImage:
            api_images = api_client.get_derived_image_in_image_annotation_dataset(
                str(dataset_uuid)
            )

    return api_images


def find_associated_objects(
    typed_associations: set,
    directory_path: Path,
    object_type: Type[bia_data_model.UserIdentifiedObject],
) -> List[bia_data_model.UserIdentifiedObject]:
    linked_object = []

    if len(typed_associations) == 0:
        return linked_object

    # We read all the e.g. Biosamples multiple times per study because there aren't that many and their json is small
    typed_object_in_study: List[bia_data_model.UserIdentifiedObject] = read_all_json(
        directory_path, object_type
    )
    for object in typed_object_in_study:
        if object.title_id in typed_associations:
            linked_object.append(object)
    return linked_object


def retrieve_detail_objects(
    dataset: api_models.ExperimentalImagingDataset,
    detail_map: dict,
    context: StudyCLIContext,
) -> dict[str, List]:
    if context.root_directory:
        detail_fields = {}

        association_by_type = {
            "biosample": set(),
            "image_acquisition": set(),
            "specimen": set(),
        }
        for association in dataset.attribute["associations"]:
            for key in association_by_type.keys():
                association_by_type[key].add(association[key])

        for field, source_info in detail_map.items():
            detail_path = context.root_directory.joinpath(
                f"{source_info['source_directory']}/{context.accession_id}/*.json"
            )
            api_objects = find_associated_objects(
                association_by_type[source_info["association_field"]],
                detail_path,
                source_info["bia_type"],
            )
            detail_fields[field] = api_objects

    else:
        # Currently performing graph traversal of:
        # Dataset -> Images[0] -> specimen -> details (while all images have all the same specimen info)
        # but could alternatively switch to the much simpler (for the exporter!):
        # Dataset -> details field (when we have multi-hop api endpoints)
        dataset_images = api_client.get_experimentally_captured_image_in_experimental_imaging_dataset(
            str(dataset.uuid)
        )

        acquisition_process = []
        biological_entity = []
        specimen_imaging_preparation_protocol = []
        specimen_growth_protocol = []

        if len(dataset_images) != 0:
            single_dataset_image = dataset_images[0]

            for ia_uuid in single_dataset_image.acquisition_process_uuid:
                acquisition_process.append(
                    api_client.get_image_acquisition(str(ia_uuid))
                )

            specimen = api_client.get_specimen(str(single_dataset_image.subject_uuid))

            for biosample_uuid in specimen.sample_of_uuid:
                biological_entity.append(api_client.get_bio_sample(str(biosample_uuid)))
            for sipp_uuid in specimen.imaging_preparation_protocol_uuid:
                specimen_imaging_preparation_protocol.append(
                    api_client.get_specimen_imaging_preparation_protocol(str(sipp_uuid))
                )
            for sgp_uuid in specimen.growth_protocol_uuid:
                specimen_growth_protocol.append(
                    api_client.get_specimen_growth_protocol(str(sgp_uuid))
                )

        # TODO: Use detail map to namage field names in a single place
        detail_fields = {
            "acquisition_process": acquisition_process,
            "biological_entity": biological_entity,
            "specimen_imaging_preparation_protocol": specimen_imaging_preparation_protocol,
            "specimen_growth_protocol": specimen_growth_protocol,
        }

    return detail_fields


def retrieve_image_annotatation_datasets(
    context: StudyCLIContext,
) -> List[api_models.ImageAnnotationDataset]:
    if context.root_directory:
        iad_directory = context.root_directory.joinpath(
            f"image_annotation_datasets/{context.accession_id}/*.json"
        )

        api_aids: List[api_models.ImageAnnotationDataset] = read_all_json(
            iad_directory, api_models.ImageAnnotationDataset
        )
    else:
        api_aids = api_client.get_image_annotation_dataset_in_study(
            str(context.study_uuid)
        )

    return api_aids


def retrieve_annotion_method(
    api_dataset: api_models.ImageAnnotationDataset, context: StudyCLIContext
):
    if context.root_directory:
        api_methods = []
        methods_directory = context.root_directory.joinpath(
            f"annotation_methods/{context.accession_id}/*.json"
        )
        all_api_methods: List[api_models.AnnotationMethod] = read_all_json(
            methods_directory, api_models.AnnotationMethod
        )
        for api_method in all_api_methods:
            # Note that currently the title_ids are the same because the two objects are created from the same user input.
            if api_method.title_id == api_dataset.title_id:
                api_methods.append(api_method)
    else:
        # Currently performing graph traversal of:
        # Dataset -> Derived Images[0] -> annotation_method (while all images have all the same info)
        # but could alternatively switch to the much simpler (for the exporter!):
        # Dataset -> annotation_method field (when we have multi-hop api endpoints)

        dataset_images = api_client.get_derived_image_in_image_annotation_dataset(
            str(api_dataset.uuid)
        )

        api_methods = []
        if len(dataset_images) != 0:
            single_dataset_image = dataset_images[0]
            for method_uuid in single_dataset_image.creation_process_uuid:
                api_methods.append(api_client.get_annotation_method(str(method_uuid)))

    return api_methods

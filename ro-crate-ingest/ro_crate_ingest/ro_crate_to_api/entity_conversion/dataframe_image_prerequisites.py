import pandas as pd
from bia_shared_datamodels.package_specific_uuid_creation import (
    shared,
    ro_crate_uuid_creation,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
import bia_integrator_api.models as APIModels
from bia_shared_datamodels import ro_crate_models
import logging
import numpy as np
from urllib.parse import quote
from concurrent.futures import ProcessPoolExecutor
from functools import partial

logger = logging.getLogger("__main__." + __name__)


def prepare_all_ids_for_images(
    image_dataframe: pd.DataFrame,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
    max_workers: int,
) -> tuple[pd.DataFrame, dict[str, str]]:
    result_data_by_id: pd.DataFrame = image_dataframe.groupby(
        "result_data_id", dropna=True
    )

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(
            executor.map(
                partial(
                    prep_image_data_row,
                    crate_objects_by_id=crate_objects_by_id,
                    study_uuid=study_uuid,
                ),
                result_data_by_id,
            )
        )

    result_data_uuid_dataframe = pd.DataFrame(results)

    result_data_id_uuid_map = dict(
        zip(
            result_data_uuid_dataframe["result_data_id"],
            result_data_uuid_dataframe["result_data_uuid"],
        )
    )

    return result_data_uuid_dataframe, result_data_id_uuid_map


def prep_image_data_row(
    group_df: pd.DataFrame,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
):
    import pandas as pd
    from numpy import nan

    result_data_id = group_df[0]
    df = group_df[1]
    file_uuids = list(df["file_ref_uuid"])

    obj_type = df["result_type"].iloc[0]
    if obj_type == "http://bia/Image":
        result_data_uuid, result_data_uuid_attribute = shared.create_image_uuid(
            study_uuid, file_uuids, APIModels.Provenance.BIA_INGEST
        )
    elif obj_type == "http://bia/AnnotationData":
        result_data_uuid, result_data_uuid_attribute = (
            shared.create_annotation_data_uuid(
                study_uuid, file_uuids, APIModels.Provenance.BIA_INGEST
            )
        )
    else:
        raise ValueError(
            f"Expected {result_data_id} to be of type http://bia/Image or http://bia/AnnotationData, but fount: {obj_type}"
        )

    result_data_label = None
    creation_process_id = None
    creation_process_uuid = None
    creation_process_uuid_attr = None
    specimen_id = None
    specimen_uuid = None
    specimen_uuid_attr = None
    annotation_method_id = None
    image_acquisition_protocol_id = None
    protocol_id = None
    bio_sample_id = None
    specimen_imaging_preparation_protocol_id = None
    specimen_uuid = None
    roc_creation_process_input_image = None

    # Use ro-crate creation process, if provided
    if result_data_id in crate_objects_by_id:
        roc_image: ro_crate_models.Image = crate_objects_by_id[result_data_id]
        result_data_label = roc_image.label
        if roc_image.resultOf:
            creation_process_id = roc_image.resultOf.id
            creation_process: ro_crate_models.CreationProcess = crate_objects_by_id[
                creation_process_id
            ]
            creation_process_uuid, creation_process_uuid_attr = (
                ro_crate_uuid_creation.create_creation_process_uuid(
                    study_uuid, creation_process_id
                )
            )
            if creation_process.subject:
                specimen_id = creation_process.subject.id

            roc_creation_process_input_image = [
                x.id for x in creation_process.inputImage
            ]
            annotation_method_id = [x.id for x in creation_process.annotationMethod]
            protocol_id = [x.id for x in creation_process.protocol]
            image_acquisition_protocol_id = [
                x.id for x in creation_process.imageAcquisitionProtocol
            ]

    # TODO: should use file-list level association information prior to falling back to dataset

    # Fallback to using dataset association values
    dataset_id = flatten_set_of_same_values(df["dataset_roc_id"])
    if not creation_process_id:
        dataset: ro_crate_models.Dataset = crate_objects_by_id[quote(dataset_id)]

        annotation_method_id = [x.id for x in dataset.associatedAnnotationMethod]
        image_acquisition_protocol_id = [
            x.id for x in dataset.associatedImageAcquisitionProtocol
        ]
        protocol_id = [x.id for x in dataset.associatedProtocol]
        bio_sample_id = [x.id for x in dataset.associatedBiologicalEntity]
        specimen_imaging_preparation_protocol_id = [
            x.id for x in dataset.associatedSpecimenImagingPreparationProtocol
        ]

        specimen_id = (
            dataset.associatedSpecimen.id if dataset.associatedSpecimen else None
        )

    # If specimen was provided, use specimen's info instead of dataset
    if specimen_id:
        specimen: ro_crate_models.Specimen = crate_objects_by_id[specimen_id]
        bio_sample_id = [x.id for x in specimen.biologicalEntity]
        specimen_imaging_preparation_protocol_id = [
            x.id for x in specimen.imagingPreparationProtocol
        ]
        specimen_uuid, specimen_uuid_attr = ro_crate_uuid_creation.create_specimen_uuid(
            study_uuid, specimen_id
        )

    if (
        not specimen_id
        and any([bio_sample_id, specimen_imaging_preparation_protocol_id])
        and (
            len(bio_sample_id) > 0 or len(specimen_imaging_preparation_protocol_id) > 0
        )
    ):
        specimen_uuid, specimen_uuid_attr = shared.create_specimen_uuid(
            study_uuid, result_data_uuid, APIModels.Provenance.BIA_INGEST
        )
    if not creation_process_id:
        creation_process_uuid, creation_process_uuid_attr = (
            shared.create_creation_process_uuid(
                study_uuid, result_data_uuid, APIModels.Provenance.BIA_INGEST
            )
        )

    # Sort out source image ids:
    source_image_ids = set()
    for source_img_list in df["source_image_id_from_filelist"]:
        if isinstance(source_img_list, list):
            [source_image_ids.add(source_img_id) for source_img_id in source_img_list]
    source_image_id_from_filelist = sorted(list(source_image_ids))
    if source_image_id_from_filelist and roc_creation_process_input_image:
        source_image_id = roc_creation_process_input_image.extend(
            source_image_id_from_filelist
        )
    elif source_image_id_from_filelist:
        source_image_id = source_image_id_from_filelist
    elif roc_creation_process_input_image:
        source_image_id = roc_creation_process_input_image
    else:
        source_image_id = np.nan

    filelist_label_index = df["result_data_label_from_filelist"].first_valid_index()
    if not result_data_label and filelist_label_index:
        result_data_label = str(
            df["result_data_label_from_filelist"].loc[filelist_label_index]
        )

    return pd.Series(
        {
            "file_ref_uuids": file_uuids,
            "dataset_roc_id": dataset_id,
            "dataset_uuid": flatten_set_of_same_values(df["dataset_uuid"]),
            "result_data_id": flatten_set_of_same_values(df["result_data_id"]),
            "result_type": obj_type,
            "result_data_uuid": str(result_data_uuid),
            "result_data_label": result_data_label,
            "result_data_uuid_attribute": result_data_uuid_attribute.model_dump(),
            "source_image_id_from_filelist": source_image_id,
            "creation_process_id": creation_process_id,
            "creation_process_uuid": str(creation_process_uuid),
            "creation_process_uuid_attr": creation_process_uuid_attr.model_dump(),
            "specimen_id": specimen_id,
            "specimen_uuid": (str(specimen_uuid) if specimen_uuid else None),
            "specimen_uuid_attr": (
                specimen_uuid_attr.model_dump() if specimen_uuid_attr else None
            ),
            "annotation_method_id": annotation_method_id,
            "image_acquisition_protocol_id": image_acquisition_protocol_id,
            "protocol_id": protocol_id,
            "bio_sample_id": bio_sample_id,
            "specimen_imaging_preparation_protocol_id": specimen_imaging_preparation_protocol_id,
        }
    )


def flatten_set_of_same_values(column: pd.Series):
    values = column.unique()
    if len(values) != 1:
        logger.warning("More than 1 unique value in image column")

    return values[0]

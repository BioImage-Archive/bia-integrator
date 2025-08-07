import pandas as pd
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_file_reference_uuid,
    create_image_uuid,
)
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
    create_specimen_uuid,
)
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

logger = logging.getLogger("__main__." + __name__)


# Recieves:
# {
#         "path": row["path"],
#         "file_ref_uuid": str(uuid),
#         "dataset_roc_id": dataset_roc_id,
#         "dataset_uuid": dataset_uuid,
#         "image_id": image_id,
#         "source_image_id_from_filelist": file_list_source_image_id,
#     }


def prepare_all_ids_for_images(
    image_dataframe: pd.DataFrame,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
) -> tuple[pd.DataFrame, dict[str, str]]:
    image_uuid_dataframe: pd.DataFrame = image_dataframe.groupby(
        "image_id", dropna=True
    ).apply(
        prep_image_data_row,
        crate_objects_by_id,
        study_uuid,
    )
    image_id_uuid_map = dict(
        zip(image_uuid_dataframe["image_id"], image_uuid_dataframe["image_uuid"])
    )

    return image_uuid_dataframe, image_id_uuid_map


def prep_image_data_row(
    df: pd.DataFrame, crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
):
    file_uuids = list(df["file_ref_uuid"])
    image_uuid, image_uuid_attribute = shared.create_image_uuid(
        study_uuid, file_uuids, APIModels.Provenance.BIA_INGEST
    )

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
    image_id = df["image_id"].unique()[0]
    if image_id in crate_objects_by_id:
        roc_image: ro_crate_models.Image = crate_objects_by_id[image_id]
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
        bio_sample_id = [x.id for x in dataset.associatedImageAcquisitionProtocol]
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
            study_uuid, image_uuid, APIModels.Provenance.BIA_INGEST
        )
    if not creation_process_id:
        creation_process_uuid, creation_process_uuid_attr = (
            shared.create_creation_process_uuid(
                study_uuid, image_uuid, APIModels.Provenance.BIA_INGEST
            )
        )

    # Sort out source image ids:
    source_image_id_from_filelist = (
        df["source_image_id_from_filelist"].dropna().unique()
        if len(df["source_image_id_from_filelist"].dropna().unique()) > 0
        else None
    )
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

    return pd.Series(
        {
            "file_ref_uuids": file_uuids,
            "dataset_roc_id": dataset_id,
            "dataset_uuid": flatten_set_of_same_values(df["dataset_uuid"]),
            "image_id": flatten_set_of_same_values(df["image_id"]),
            "image_uuid": str(image_uuid),
            "image_uuid_attribute": image_uuid_attribute.model_dump(),
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

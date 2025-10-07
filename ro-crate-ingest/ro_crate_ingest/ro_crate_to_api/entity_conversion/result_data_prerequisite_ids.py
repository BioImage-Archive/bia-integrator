import pandas as pd
import pandas.api.typing as pdtypes
import logging

from bia_shared_datamodels.package_specific_uuid_creation import (
    shared,
    ro_crate_uuid_creation,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import ro_crate_models
import bia_integrator_api.models as APIModels
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
    result_data_by_id: pdtypes.DataFrameGroupBy = image_dataframe.groupby(
        "result_data_id", dropna=True
    )

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(
            executor.map(
                partial(
                    prep_result_data_row,
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


def prep_result_data_row(
    group_df: tuple[str, pd.DataFrame],
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
):
    import pandas as pd
    from numpy import nan

    result_data_id = group_df[0]
    df = group_df[1]

    pre_requisite_ids_row = {
        "file_ref_uuids": list(df["file_ref_uuid"]),
        "dataset_roc_id": flatten_set_of_same_values(df["dataset_roc_id"]),
        "dataset_uuid": flatten_set_of_same_values(df["dataset_uuid"]),
        "result_data_id": result_data_id,
        "result_type": df["result_type"].iloc[0],
        "result_data_uuid": None,
        "result_data_label": None,
        "result_data_uuid_attr": None,
        "source_image_id": [],
        "creation_process_id": None,
        "creation_process_uuid": None,
        "creation_process_uuid_attr": None,
        "specimen_id": None,
        "specimen_uuid": None,
        "specimen_uuid_attr": None,
        "annotation_method_id": [],
        "image_acquisition_protocol_id": [],
        "protocol_id": [],
        "bio_sample_id": [],
        "specimen_imaging_preparation_protocol_id": [],
        "original_file_ref_total_size": 0,
        "original_file_ref_file_format": None,
        "original_file_ref_uri": [],
        "image_rep_uuid": None,
        "image_rep_uuid_attr": None,
    }

    get_result_data_uuids(result_data_id, study_uuid, pre_requisite_ids_row)

    # Assuming all rows are the the same
    association_data_from_filelist = df["association_data_from_filelist"].iloc[0]
    dataset: ro_crate_models.Dataset = crate_objects_by_id[
        quote(pre_requisite_ids_row["dataset_roc_id"])
    ]

    if result_data_id in crate_objects_by_id:
        get_result_data_from_ro_crate(
            crate_objects_by_id, result_data_id, pre_requisite_ids_row
        )
    else:
        filelist_label_index = df["result_data_label_from_filelist"].first_valid_index()
        if filelist_label_index != None:
            pre_requisite_ids_row["result_data_label"] = str(
                df["result_data_label_from_filelist"].loc[filelist_label_index]
            )

    # Use ro-crate creation process, if provided, otherwise create one using information from association.
    if pre_requisite_ids_row["creation_process_id"]:
        creation_process: ro_crate_models.CreationProcess = crate_objects_by_id[
            pre_requisite_ids_row["creation_process_id"]
        ]
        creation_process_uuid, creation_process_uuid_attr = (
            ro_crate_uuid_creation.create_creation_process_uuid(
                study_uuid, creation_process.id
            )
        )
        pre_requisite_ids_row["creation_process_uuid"] = str(creation_process_uuid)
        pre_requisite_ids_row["creation_process_uuid_attr"] = (
            creation_process_uuid_attr.model_dump()
        )
        get_creation_process_dependencies_from_ro_crate(
            creation_process, pre_requisite_ids_row
        )
    else:
        creation_process_uuid, creation_process_uuid_attr = (
            shared.create_creation_process_uuid(
                study_uuid,
                pre_requisite_ids_row["result_data_uuid"],
                APIModels.Provenance.BIA_INGEST,
            )
        )
        pre_requisite_ids_row["creation_process_uuid"] = str(creation_process_uuid)
        pre_requisite_ids_row["creation_process_uuid_attr"] = (
            creation_process_uuid_attr.model_dump()
        )
        get_creation_process_info_from_associations(
            association_data_from_filelist, dataset, pre_requisite_ids_row
        )

        # TODO handle image dependencies

    # Use ro-crate specimen, if provided, otherwise check to see if associations have a biosample or a specimen imaging preparation & create one if it has either.
    if pre_requisite_ids_row["specimen_id"]:
        specimen: ro_crate_models.Specimen = crate_objects_by_id[
            pre_requisite_ids_row["specimen_id"]
        ]
        specimen_uuid, specimen_uuid_attr = ro_crate_uuid_creation.create_specimen_uuid(
            study_uuid, pre_requisite_ids_row["specimen_id"]
        )
        pre_requisite_ids_row["specimen_uuid"] = str(specimen_uuid)
        pre_requisite_ids_row["specimen_uuid_attr"] = specimen_uuid_attr.model_dump()
        get_specimen_dependencies_from_ro_crate(specimen, pre_requisite_ids_row)

    else:
        get_specimen_dependencies_from_associations(
            association_data_from_filelist, dataset, pre_requisite_ids_row
        )
        if (
            len(pre_requisite_ids_row["bio_sample_id"]) > 0
            and len(pre_requisite_ids_row["specimen_imaging_preparation_protocol_id"])
            > 0
        ):
            specimen_uuid, specimen_uuid_attr = shared.create_specimen_uuid(
                study_uuid,
                pre_requisite_ids_row["result_data_uuid"],
                APIModels.Provenance.BIA_INGEST,
            )
            pre_requisite_ids_row["specimen_uuid"] = str(specimen_uuid)
            pre_requisite_ids_row["specimen_uuid_attr"] = (
                specimen_uuid_attr.model_dump()
            )

    # Add information for first image representation if the result data is an Image.
    if pre_requisite_ids_row["result_type"] == "http://bia/Image":
        image_rep_uuid, image_rep_uuid_attr = shared.create_image_representation_uuid(
            study_uuid,
            pre_requisite_ids_row["result_data_uuid"],
            APIModels.Provenance.BIA_INGEST,
        )
        pre_requisite_ids_row |= {
            "original_file_ref_total_size": int(df["size_in_bytes"].sum()),
            "original_file_ref_format": df["file_format"].iloc[0],
            "original_file_ref_uri": df["uri"].to_list(),
            "image_rep_uuid": str(image_rep_uuid),
            "image_rep_uuid_attr": image_rep_uuid_attr.model_dump(),
        }

    return pd.Series(pre_requisite_ids_row)


def flatten_set_of_same_values(column: pd.Series):
    values = column.unique()
    if len(values) != 1:
        logger.warning("More than 1 unique value in image column")

    return values[0]


def get_result_data_uuids(
    result_data_id: str, study_uuid: str, pre_requisite_ids_row: dict
) -> None:
    obj_type = pre_requisite_ids_row["result_type"]
    if obj_type == "http://bia/Image":
        result_data_uuid, result_data_uuid_attribute = shared.create_image_uuid(
            study_uuid,
            pre_requisite_ids_row["file_ref_uuids"],
            APIModels.Provenance.BIA_INGEST,
        )
    elif obj_type == "http://bia/AnnotationData":
        result_data_uuid, result_data_uuid_attribute = (
            shared.create_annotation_data_uuid(
                study_uuid,
                pre_requisite_ids_row["file_ref_uuids"],
                APIModels.Provenance.BIA_INGEST,
            )
        )
    else:
        raise ValueError(
            f"Expected {result_data_id} to be of type http://bia/Image or http://bia/AnnotationData, but fount: {obj_type}"
        )

    pre_requisite_ids_row["result_data_uuid"] = str(result_data_uuid)
    pre_requisite_ids_row["result_data_uuid_attr"] = (
        result_data_uuid_attribute.model_dump()
    )


def get_result_data_from_ro_crate(
    crate_objects_by_id: dict[str, ROCrateModel],
    result_data_id: str,
    pre_requisite_ids_row: dict,
) -> None:
    roc_result_data: ro_crate_models.Image | ro_crate_models.AnnotationData = (
        crate_objects_by_id[result_data_id]
    )
    pre_requisite_ids_row["result_data_label"] = roc_result_data.label
    if roc_result_data.resultOf:
        pre_requisite_ids_row["creation_process_id"] = roc_result_data.resultOf.id


def get_creation_process_dependencies_from_ro_crate(
    creation_process: ro_crate_models.CreationProcess,
    pre_requisite_ids_row: dict,
):
    if creation_process.subject:
        pre_requisite_ids_row["specimen_id"] = creation_process.subject.id
    pre_requisite_ids_row["source_image_id"] = [
        x.id for x in creation_process.inputImage
    ]
    pre_requisite_ids_row["annotation_method_id"] = [
        x.id for x in creation_process.annotationMethod
    ]
    pre_requisite_ids_row["protocol_id"] = [x.id for x in creation_process.protocol]
    pre_requisite_ids_row["image_acquisition_protocol_id"] = [
        x.id for x in creation_process.imageAcquisitionProtocol
    ]


def get_creation_process_info_from_associations(
    association_data_from_filelist: dict,
    dataset: ro_crate_models.Dataset,
    pre_requisite_ids_row: dict,
) -> None:
    """
    For each field in the creation process, use the file list information if the column was included in the file list.
    If the column was not included, use the dataset's association.
    """

    field_id_mapping = [
        ("associatedImageAcquisitionProtocol", "image_acquisition_protocol_id"),
        ("associatedProtocol", "protocol_id"),
        ("associatedAnnotationMethod", "annotation_method_id"),
    ]

    map_list_field_from_association(
        association_data_from_filelist, dataset, pre_requisite_ids_row, field_id_mapping
    )

    # specimen is not a list field
    if (
        association_data_from_filelist
        and "http://bia/associatedSubject" in association_data_from_filelist
    ):
        pre_requisite_ids_row["specimen_id"] = association_data_from_filelist[
            "http://bia/associatedSubject"
        ]
    elif dataset.associatedSpecimen:
        pre_requisite_ids_row["specimen_id"] = dataset.associatedSpecimen.id

    # There is no associatedInputImage on datasets for now, since it seems unlikely a whole dataset would annotate a single iamge.
    if (
        association_data_from_filelist
        and "http://bia/associatedInputImage" in association_data_from_filelist
    ):
        pre_requisite_ids_row["source_image_id"] = association_data_from_filelist[
            "http://bia/associatedInputImage"
        ]


def get_specimen_dependencies_from_associations(
    association_data_from_filelist: dict,
    dataset: ro_crate_models.Dataset,
    pre_requisite_ids_row: dict,
) -> None:

    field_id_mapping = [
        ("associatedBiologicalEntity", "bio_sample_id"),
        (
            "associatedSpecimenImagingPreparationProtocol",
            "specimen_imaging_preparation_protocol_id",
        ),
    ]

    map_list_field_from_association(
        association_data_from_filelist, dataset, pre_requisite_ids_row, field_id_mapping
    )


def get_specimen_dependencies_from_ro_crate(
    specimen: ro_crate_models.Specimen,
    pre_requisite_ids_row: dict,
) -> None:
    pre_requisite_ids_row["bio_sample_id"] = [x.id for x in specimen.biologicalEntity]
    pre_requisite_ids_row["specimen_imaging_preparation_protocol_id"] = [
        x.id for x in specimen.imagingPreparationProtocol
    ]


def map_list_field_from_association(
    association_data_from_filelist: dict,
    dataset: ro_crate_models.Dataset,
    pre_requisite_ids_row: dict,
    field_id_mapping: list[tuple],
) -> None:
    for ro_crate_name, row_field in field_id_mapping:
        property_uri = f"http://bia/{ro_crate_name}"
        if row_field == "specimen_imaging_preparation_protocol_id":
            property_uri = "http://bia/associatedImagingPreparationProtocol"

        if (
            association_data_from_filelist
            and property_uri in association_data_from_filelist
        ):
            pre_requisite_ids_row[row_field] = association_data_from_filelist[
                property_uri
            ]
        else:
            pre_requisite_ids_row[row_field] = [
                x.id for x in getattr(dataset, ro_crate_name)
            ]

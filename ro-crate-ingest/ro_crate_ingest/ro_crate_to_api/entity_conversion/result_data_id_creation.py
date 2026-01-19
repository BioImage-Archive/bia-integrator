import pandas as pd
import pandas.api.typing as pdtypes
import logging

from bia_shared_datamodels.package_specific_uuid_creation import (
    shared,
    ro_crate_uuid_creation,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import ro_crate_models, attribute_models
import bia_integrator_api.models as APIModels
from urllib.parse import quote
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from rdflib import RDF
from uuid import UUID

logger = logging.getLogger("__main__." + __name__)


def prepare_all_ids_for_result_data(
    typed_object_dataframe: pd.DataFrame,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
    max_workers: int,
) -> tuple[pd.DataFrame, dict[str, str]]:
    result_data_by_id: pdtypes.DataFrameGroupBy = typed_object_dataframe.groupby(
        "http://schema.org/name", dropna=True
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
            result_data_uuid_dataframe["result_data_name"],
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

    result_data_label = group_df[0]
    df = group_df[1]

    result_type = flatten_set_of_same_values(df[str(RDF.type)])
    dataset_uuid = flatten_set_of_same_values(df["http://schema.org/isPartOf"])
    file_reference_uuids = list(df["http://purl.org/dc/terms/identifier"])
    result_data_uuid, result_data_uuid_attr = create_result_data_uuid(
        result_type, file_reference_uuids, study_uuid
    )

    pre_requisite_ids_row = {
        "file_ref_uuids": file_reference_uuids,
        "dataset_uuid": dataset_uuid,
        "result_type": result_type,
        "result_data_name": result_data_label,
        "result_data_uuid": str(result_data_uuid),
        "result_data_uuid_attr": result_data_uuid_attr.model_dump(),
        "creation_process_uuid": None,
        "creation_process_uuid_attr": None,
        "original_file_ref_total_size": int(df["http://bia/sizeInBytes"].sum()),
        "original_file_ref_format": flatten_set_of_same_values(
            df["http://purl.org/dc/terms/hasFormat"]
        ),
        "original_file_ref_uri": list(df["http://bia/uri"]),
        "specimen_id": None,
        "specimen_uuid": None,
        "specimen_uuid_attr": None,
        "source_image_name": [],
        "annotation_method_id": [],
        "image_acquisition_protocol_id": [],
        "protocol_id": [],
        "bio_sample_id": [],
        "specimen_imaging_preparation_protocol_id": [],
        "image_rep_uuid": None,
        "image_rep_uuid_attr": None,
    }

    if len(df["http://bia/associatedCreationProcess"].dropna()) != 0:
        creation_process_roc_id = flatten_set_of_same_values(
            df["http://bia/associatedCreationProcess"]
        )

        populate_from_creation_process(
            pre_requisite_ids_row,
            creation_process_roc_id,
            crate_objects_by_id,
            study_uuid,
        )

    else:
        populate_creation_process_info_from_columns(
            study_uuid, df, result_data_uuid, pre_requisite_ids_row
        )

        if len(df["http://bia/associatedSubject"].dropna()) != 0:
            specimen_roc_id = flatten_set_of_same_values(
                df["http://bia/associatedCreationProcess"]
            )
            populate_from_specimen(
                pre_requisite_ids_row,
                specimen_roc_id,
                crate_objects_by_id,
                study_uuid,
            )
        elif has_biosample_or_imaging_preparation_protocol(df):
            populate_specimen_info_from_columns(
                study_uuid, df, result_data_uuid, pre_requisite_ids_row
            )

    if result_type == "http://bia/Image":
        image_rep_uuid, image_rep_uuid_attr = shared.create_image_representation_uuid(
            study_uuid, str(result_data_uuid), APIModels.Provenance.BIA_INGEST
        )
        pre_requisite_ids_row["image_rep_uuid"] = str(image_rep_uuid)
        pre_requisite_ids_row["image_rep_uuid_attr"] = image_rep_uuid_attr.model_dump()

    return pre_requisite_ids_row


def populate_specimen_info_from_columns(
    study_uuid, df, result_data_uuid, pre_requisite_ids_row
):
    specimen_uuid, specimen_uuid_attr = shared.create_specimen_uuid(
        study_uuid, result_data_uuid, APIModels.Provenance.BIA_INGEST
    )
    pre_requisite_ids_row["specimen_uuid"] = str(specimen_uuid)
    pre_requisite_ids_row["specimen_uuid_attr"] = specimen_uuid_attr.model_dump()

    pre_requisite_ids_row["bio_sample_id"] = collect_association_list_values(
        df["http://bia/associatedBiologicalEntity"]
    )

    pre_requisite_ids_row["specimen_imaging_preparation_protocol_id"] = (
        collect_association_list_values(
            df["http://bia/associatedImagingPreparationProtocol"]
        )
    )


def populate_creation_process_info_from_columns(
    study_uuid, df, result_data_uuid, pre_requisite_ids_row
):
    creation_process_uuid, creation_process_uuid_attr = (
        shared.create_creation_process_uuid(
            study_uuid, result_data_uuid, APIModels.Provenance.BIA_INGEST
        )
    )
    pre_requisite_ids_row["creation_process_uuid"] = str(creation_process_uuid)
    pre_requisite_ids_row["creation_process_uuid_attr"] = (
        creation_process_uuid_attr.model_dump()
    )

    pre_requisite_ids_row["annotation_method_id"] = collect_association_list_values(
        df["http://bia/associatedAnnotationMethod"]
    )
    pre_requisite_ids_row["image_acquisition_protocol_id"] = (
        collect_association_list_values(
            df["http://bia/associatedImageAcquisitionProtocol"]
        )
    )
    pre_requisite_ids_row["protocol_id"] = collect_association_list_values(
        df["http://bia/associatedProtocol"]
    )
    pre_requisite_ids_row["source_image_name"] = collect_association_list_values(
        df["http://bia/associatedInputImage"]
    )


def has_biosample_or_imaging_preparation_protocol(df):
    bio_entity_count = len(
        collect_association_list_values(df["http://bia/associatedBiologicalEntity"])
    )
    sipp_count = len(
        collect_association_list_values(
            df["http://bia/associatedImagingPreparationProtocol"]
        )
    )
    return bio_entity_count > 0 or sipp_count > 0


def populate_from_creation_process(
    pre_requisite_ids_row: dict,
    creation_process_roc_id: str,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
):
    creation_process_uuid, creation_process_uuid_attr = (
        ro_crate_uuid_creation.create_creation_process_uuid(
            study_uuid, creation_process_roc_id
        )
    )
    pre_requisite_ids_row["creation_process_uuid"] = str(creation_process_uuid)
    pre_requisite_ids_row["creation_process_uuid_attr"] = (
        creation_process_uuid_attr.model_dump()
    )

    creation_process: ro_crate_models.CreationProcess = crate_objects_by_id[
        creation_process_roc_id
    ]
    if creation_process.subject:
        populate_from_specimen(
            pre_requisite_ids_row,
            creation_process.subject.id,
            crate_objects_by_id,
            study_uuid,
        )

    pre_requisite_ids_row["annotation_method_id"] = [
        x.id for x in creation_process.annotationMethod
    ]
    pre_requisite_ids_row["image_acquisition_protocol_id"] = [
        x.id for x in creation_process.imageAcquisitionProtocol
    ]
    pre_requisite_ids_row["protocol_id"] = [x.id for x in creation_process.protocol]

    # Note, im not sure if this works because how would the images ever be referenced?
    pre_requisite_ids_row["source_image_name"] = [
        x.id for x in creation_process.inputImage
    ]


def populate_from_specimen(
    pre_requisite_ids_row: dict,
    specimen_roc_id: str,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
):
    specimen_uuid, specimen_uuid_attr = ro_crate_uuid_creation.create_specimen_uuid(
        study_uuid, specimen_roc_id
    )
    pre_requisite_ids_row["specimen_uuid"] = str(specimen_uuid)
    pre_requisite_ids_row["specimen_uuid_attr"] = specimen_uuid_attr.model_dump()

    specimen: ro_crate_models.Specimen = crate_objects_by_id[specimen_roc_id]

    pre_requisite_ids_row["bio_sample_id"] = [x.id for x in specimen.biologicalEntity]

    pre_requisite_ids_row["specimen_imaging_preparation_protocol_id"] = [
        x.id for x in specimen.imagingPreparationProtocol
    ]


def create_result_data_uuid(
    result_data_type: str, file_refernce_uuids: list[str], study_uuid: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    match result_data_type:
        case "http://bia/Image":
            return shared.create_image_uuid(
                study_uuid, file_refernce_uuids, APIModels.Provenance.BIA_INGEST
            )
        case "http://bia/AnnotationData":
            return shared.create_annotation_data_uuid(
                study_uuid, file_refernce_uuids, APIModels.Provenance.BIA_INGEST
            )
        case _:
            raise ValueError(f"Unexpected type for result data: {result_data_type}")


def flatten_set_of_same_values(column: pd.Series):
    values = column.unique()
    if len(values) > 1:
        raise ValueError(f"More than 1 unique value in column: {values}")

    return values[0]


def collect_association_list_values(column: pd.Series):
    # Currently just returns the first value
    return column.iloc[0]

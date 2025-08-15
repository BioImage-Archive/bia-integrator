import pandas as pd

from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_bio_sample_uuid,
    create_specimen_imaging_preparation_protocol_uuid,
    create_protocol_uuid,
    create_image_acquisition_protocol_uuid,
    create_annotation_method_uuid,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
import bia_integrator_api.models as APIModels
from ro_crate_ingest.save_utils import PersistenceMode, persist

from concurrent.futures import ProcessPoolExecutor
from functools import partial

import logging

logger = logging.getLogger("__main__." + __name__)


def create_images_and_dependencies(
    result_data_dataframe: pd.DataFrame,
    crate_objects_by_id: dict[str, ROCrateModel],
    result_data_id_uuid_map: dict[str, str],
    study_uuid: str,
    accession_id: str,
    persistence_mode: PersistenceMode,
    max_workers: int = None,
) -> pd.DataFrame:

    specimens_by_group = [
        (uuid, group_df)
        for uuid, group_df in result_data_dataframe.groupby(
            "specimen_uuid", dropna=True
        )
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        r = list(
            executor.map(
                partial(
                    create_specimen_from_group,
                    study_uuid=study_uuid,
                    accession_id=accession_id,
                    persistence_mode=persistence_mode,
                ),
                specimens_by_group,
            )
        )

    base_objects = result_data_dataframe[
        result_data_dataframe["source_image_id_from_filelist"].isna()
    ]
    objects_with_image_dependencies = result_data_dataframe.dropna(
        subset=["source_image_id_from_filelist"]
    )

    # Process images & creation processes without any dependencies first

    base_creation_process_by_group = [
        (uuid, group_df)
        for uuid, group_df in base_objects.groupby("creation_process_uuid")
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        r = list(
            executor.map(
                partial(
                    create_creation_process,
                    study_uuid=study_uuid,
                    accession_id=accession_id,
                    persistence_mode=persistence_mode,
                    image_id_uuid_map=result_data_id_uuid_map,
                ),
                base_creation_process_by_group,
            )
        )

    base_images_rows = base_objects[
        base_objects["result_type"] == "http://bia/Image"
    ].to_dict("records")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        r = list(
            executor.map(
                partial(
                    create_image,
                    accession_id=accession_id,
                    persistence_mode=persistence_mode,
                ),
                base_images_rows,
            )
        )

    # This is likely to be empty most times
    base_annotation_rows = base_objects[
        base_objects["result_type"] == "http://bia/AnnotationData"
    ].to_dict("records")
    if len(base_annotation_rows) > 0:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            r = list(
                executor.map(
                    partial(
                        create_annotation_data,
                        accession_id=accession_id,
                        persistence_mode=persistence_mode,
                    ),
                    base_annotation_rows,
                )
            )

    # Then process images & creation processes with any dependencies
    # NOTE!!! This does not account for order for dependencies chains > 1. So this could fail when pushing objects to the API in such a case.

    dependent_creation_process_by_group = [
        (uuid, group_df)
        for uuid, group_df in objects_with_image_dependencies.groupby(
            "creation_process_uuid"
        )
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        r = list(
            executor.map(
                partial(
                    create_creation_process,
                    study_uuid=study_uuid,
                    accession_id=accession_id,
                    persistence_mode=persistence_mode,
                    image_id_uuid_map=result_data_id_uuid_map,
                ),
                dependent_creation_process_by_group,
            )
        )

    images_with_image_dependencies_rows = objects_with_image_dependencies[
        objects_with_image_dependencies["result_type"] == "http://bia/Image"
    ].to_dict("records")
    if len(images_with_image_dependencies_rows) > 0:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            r = list(
                executor.map(
                    partial(
                        create_image,
                        accession_id=accession_id,
                        persistence_mode=persistence_mode,
                    ),
                    images_with_image_dependencies_rows,
                )
            )

    annotation_data_with_image_dependencies_rows = objects_with_image_dependencies[
        objects_with_image_dependencies["result_type"] == "http://bia/AnnotationData"
    ].to_dict("records")
    if len(annotation_data_with_image_dependencies_rows) > 0:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            r = list(
                executor.map(
                    partial(
                        create_annotation_data,
                        accession_id=accession_id,
                        persistence_mode=persistence_mode,
                    ),
                    annotation_data_with_image_dependencies_rows,
                )
            )


def create_specimen_from_group(
    group: tuple[str, pd.DataFrame],
    study_uuid: str,
    accession_id: str,
    persistence_mode: PersistenceMode,
):
    import pandas as pd

    uuid = group[0]
    dataframe_group = group[1]

    # All rows in group should have the same value for the point of view of creating a specimen.
    first_entry = dataframe_group.iloc[0]

    model_dict = {
        "uuid": uuid,
        "version": 0,
        "sample_of_uuid": create_uuid_list(
            first_entry["bio_sample_id"], create_bio_sample_uuid, study_uuid
        ),
        "imaging_preparation_protocol_uuid": create_uuid_list(
            first_entry["specimen_imaging_preparation_protocol_id"],
            create_specimen_imaging_preparation_protocol_uuid,
            study_uuid,
        ),
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [first_entry["specimen_uuid_attr"]],
    }

    persist(
        accession_id,
        APIModels.Specimen,
        [APIModels.Specimen(**model_dict)],
        persistence_mode,
    )


def create_creation_process(
    group: tuple[str, pd.DataFrame],
    study_uuid: str,
    accession_id: str,
    persistence_mode: PersistenceMode,
    image_id_uuid_map: dict[str, str],
):
    import pandas as pd

    uuid = group[0]
    dataframe_group = group[1]

    # All rows in group should have the same value for the point of view of creating a creation process.
    first_entry = dataframe_group.iloc[0]

    if isinstance(first_entry["source_image_id_from_filelist"], list):
        input_image_uuid = [
            image_id_uuid_map[x] for x in first_entry["source_image_id_from_filelist"]
        ]
    else:
        input_image_uuid = []

    model_dict = {
        "uuid": uuid,
        "version": 0,
        "annotation_method_uuid": create_uuid_list(
            first_entry["annotation_method_id"],
            create_annotation_method_uuid,
            study_uuid,
        ),
        "image_acquisition_protocol_uuid": create_uuid_list(
            first_entry["image_acquisition_protocol_id"],
            create_image_acquisition_protocol_uuid,
            study_uuid,
        ),
        "protocol_uuid": create_uuid_list(
            first_entry["protocol_id"], create_protocol_uuid, study_uuid
        ),
        "subject_specimen_uuid": (
            None
            if pd.isna(first_entry["specimen_uuid"])
            else first_entry["specimen_uuid"]
        ),
        "input_image_uuid": input_image_uuid,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [first_entry["creation_process_uuid_attr"]],
    }

    persist(
        accession_id,
        APIModels.CreationProcess,
        [APIModels.CreationProcess(**model_dict)],
        persistence_mode,
    )


def create_image(
    row: dict,
    accession_id: str,
    persistence_mode: PersistenceMode,
):
    import pandas as pd

    model_dict = {
        "uuid": row["result_data_uuid"],
        "submission_dataset_uuid": row["dataset_uuid"],
        "creation_process_uuid": row["creation_process_uuid"],
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "original_file_reference_uuid": row["file_ref_uuids"],
        "additional_metadata": [row["result_data_uuid_attribute"]],
        "label": (
            row["result_data_label"] if not pd.isna(row["result_data_label"]) else None
        ),
    }

    persist(
        accession_id,
        APIModels.Image,
        [APIModels.Image(**model_dict)],
        persistence_mode,
    )


def create_uuid_list(
    object_ro_crate_id_list: list[str] | float,
    uuid_creation_function: callable,
    study_uuid: str,
):

    return [
        str(uuid_creation_function(study_uuid, obj_id)[0])
        for obj_id in object_ro_crate_id_list
    ]


def create_annotation_data(
    row: dict,
    accession_id: str,
    persistence_mode: PersistenceMode,
):
    import pandas as pd

    model_dict = {
        "uuid": row["result_data_uuid"],
        "submission_dataset_uuid": row["dataset_uuid"],
        "creation_process_uuid": row["creation_process_uuid"],
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "original_file_reference_uuid": row["file_ref_uuids"],
        "additional_metadata": [row["result_data_uuid_attribute"]],
        "label": (
            row["result_data_label"] if not pd.isna(row["result_data_label"]) else None
        ),
    }

    persist(
        accession_id,
        APIModels.AnnotationData,
        [APIModels.AnnotationData(**model_dict)],
        persistence_mode,
    )

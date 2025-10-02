import pandas as pd

from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_bio_sample_uuid,
    create_specimen_imaging_preparation_protocol_uuid,
    create_protocol_uuid,
    create_image_acquisition_protocol_uuid,
    create_annotation_method_uuid,
)
from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.package_specific_uuid_creation.shared import create_image_representation_uuid
import bia_integrator_api.models as APIModels
from ro_crate_ingest.save_utils import PersistenceMode, persist

from concurrent.futures import ProcessPoolExecutor
from functools import partial

import logging

logger = logging.getLogger("__main__." + __name__)


def create_images_and_dependencies(
    result_data_dataframe: pd.DataFrame,
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

    result_data_dataframe["dependency_chain_length"] = (
        caluclate_dependency_chain_length(result_data_dataframe)
    )
    max_dependency_chain_length = result_data_dataframe["dependency_chain_length"].max()

    for process_height in range(max_dependency_chain_length + 1):

        df = result_data_dataframe[
            result_data_dataframe["dependency_chain_length"] == process_height
        ]

        creation_process_by_group = [
            (uuid, group_df) for uuid, group_df in df.groupby("creation_process_uuid")
        ]

        result_data_by_group = df.to_dict("records")

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
                    creation_process_by_group,
                )
            )

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            r = list(
                executor.map(
                    partial(
                        create_result_data,
                        accession_id=accession_id,
                        persistence_mode=persistence_mode,
                    ),
                    result_data_by_group,
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

    if isinstance(first_entry["source_image_id"], list):
        input_image_uuid = [
            image_id_uuid_map[x] for x in first_entry["source_image_id"]
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


def create_result_data(
    row: dict,
    accession_id: str,
    persistence_mode: PersistenceMode,
):
    if row["result_type"] == ro_crate_models.Image.model_config["model_type"]:
        create_image(row, accession_id, persistence_mode)
        create_image_representation(row, accession_id, persistence_mode)
    elif (
        row["result_type"] == ro_crate_models.AnnotationData.model_config["model_type"]
    ):
        create_annotation_data(row, accession_id, persistence_mode)


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
        "additional_metadata": [row["result_data_uuid_attr"]],
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


def create_image_representation(
    row: dict,
    accession_id: str,
    persistence_mode: PersistenceMode,
):
    model_dict = {
        "uuid": row["image_rep_uuid"],
        "representation_of_uuid": row["result_data_uuid"],
        "version": 0,
        "file_uri": row["original_file_ref_uri"],
        "image_format": row["original_file_ref_format"],
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "total_size_in_bytes": row["original_file_ref_total_size"],
        "additional_metadata": [row["image_rep_uuid_attr"]],
        "image_viewer_setting": [],
    }

    persist(
        accession_id,
        APIModels.ImageRepresentation,
        [APIModels.ImageRepresentation(**model_dict)],
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
        "additional_metadata": [row["result_data_uuid_attr"]],
        # TODO: allow labels on AnnotationData
        # "label": (
        #     row["result_data_label"] if not pd.isna(row["result_data_label"]) else None
        # ),
    }

    persist(
        accession_id,
        APIModels.AnnotationData,
        [APIModels.AnnotationData(**model_dict)],
        persistence_mode,
    )


def caluclate_dependency_chain_length(df):
    """
    Calculate the longest dependency chain for a given result data (image or annotation data).
    This is always 1 more than the largest value of all of it's dependencies.
    """
    dep_map = dict(zip(df["result_data_id"], df["source_image_id"]))

    heights = {}
    visiting = set()

    def calculate_height(id):
        if id in heights:
            return heights[id]
        if id in visiting:
            raise ValueError(f"Cycle detected with {id}")
        visiting.add(id)
        deps = dep_map.get(id, [])
        height = (
            0
            if not deps
            else 1 + max(calculate_height(d) for d in deps if d in dep_map)
        )
        visiting.remove(id)
        heights[id] = height
        return height

    return df["result_data_id"].map(calculate_height).astype(int)

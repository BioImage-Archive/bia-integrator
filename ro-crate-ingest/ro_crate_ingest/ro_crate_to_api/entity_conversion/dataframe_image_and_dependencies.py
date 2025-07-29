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
from numpy import nan

logger = logging.getLogger("__main__." + __name__)


# Recieves:
# {
#        "file_ref_uuids": file_uuids,
#         "dataset_roc_id": dataset_id,
#         "dataset_uuid": flatten_set_of_same_values(df["dataset_uuid"]),
#         "image_id": flatten_set_of_same_values(df["image_id"]),
#         "image_uuid": str(image_uuid),
#         "image_uuid_attribute": image_uuid_attribute.model_dump(),
#         "source_image_id_from_filelist": df["source_image_id_from_filelist"].unique(),
# "creation_process_id": creation_process_id,
# "creation_process_uuid": str(creation_process_uuid),
# "creation_process_uuid_attr": creation_process_uuid_attr.model_dump(),
# "specimen_id": specimen_id,
# "specimen_uuid": (str(specimen_uuid) if specimen_uuid else None),
# "specimen_uuid_attr": (
#     specimen_uuid_attr.model_dump() if specimen_uuid_attr else None
# ),
# "annotation_method_id": annotation_method_id,
# "image_acquisition_protocol_id": image_acquisition_protocol_id,
# "protocol_id": protocol_id,
# "bio_sample_id": bio_sample_id,
# "specimen_imaging_preparation_protocol_id": specimen_imaging_preparation_protocol_id,
#     }


def create_images_and_dependencies(
    image_dataframe: pd.DataFrame,
    crate_objects_by_id: dict[str, ROCrateModel],
    image_id_uuid_map: dict[str, str],
    study_uuid: str,
    accession_id: str,
    persistence_mode: PersistenceMode,
    max_workers: int = None,
) -> pd.DataFrame:

    specimens_by_group = [
        (uuid, group_df)
        for uuid, group_df in image_dataframe.groupby("specimen_uuid", dropna=True)
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

    base_images = image_dataframe[
        image_dataframe["source_image_id_from_filelist"].isna()
    ]
    images_with_image_dependencies = image_dataframe.dropna(
        subset=["source_image_id_from_filelist"]
    )

    # Process images & creation processes without any dependencies first

    base_creation_process_by_group = [
        (uuid, group_df)
        for uuid, group_df in base_images.groupby("creation_process_uuid")
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        r = list(
            executor.map(
                partial(
                    create_creation_process,
                    study_uuid=study_uuid,
                    accession_id=accession_id,
                    persistence_mode=persistence_mode,
                    image_id_uuid_map=image_id_uuid_map,
                ),
                base_creation_process_by_group,
            )
        )

    base_images_rows = base_images.to_dict("records")
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

    # Then process images & creation processes with any dependencies
    # NOTE!!! This does not account for order for dependencies chains > 1. So this could fail when pushing objects to the API in such a case.

    dependent_creation_process_by_group = [
        (uuid, group_df)
        for uuid, group_df in images_with_image_dependencies.groupby(
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
                    image_id_uuid_map=image_id_uuid_map,
                ),
                dependent_creation_process_by_group,
            )
        )

    images_with_image_dependencies_rows = images_with_image_dependencies.to_dict(
        "records"
    )
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

    if not pd.isna(first_entry["source_image_id_from_filelist"]):
        input_image_uuid = [
            image_id_uuid_map.get(x)
            for x in first_entry["source_image_id_from_filelist"]
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

    model_dict = {
        "uuid": row["image_uuid"],
        "submission_dataset_uuid": row["dataset_uuid"],
        "creation_process_uuid": row["creation_process_uuid"],
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "original_file_reference_uuid": row["file_ref_uuids"],
        "additional_metadata": [row["image_uuid_attribute"]],
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

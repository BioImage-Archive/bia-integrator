from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import pathlib
import glob
import logging

logger = logging.getLogger("__main__." + __name__)


def create_file_reference(
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
    crate_path: pathlib.Path,
) -> list[APIModels.FileReference]:
    ro_crate_datasets = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Dataset)
    )

    file_reference_list = []
    for dataset in ro_crate_datasets:
        file_paths = find_files(dataset, crate_path)

        # TODO: deal with files not in datasets, and possibly edge cases like unzipped omezarrs.

        dataset_uuid = str(uuid_creation.create_dataset_uuid(dataset.id, study_uuid))

        for file_path in file_paths:
            file_reference_list.append(
                create_api_file_reference(
                    file_path, study_uuid, dataset_uuid, crate_path
                )
            )

    return file_reference_list


def find_files(dataset: ROCrateModels.Dataset, crate_path: pathlib.Path) -> list[str]:
    path_to_search = crate_path / dataset.id / "*"
    paths = glob.glob(str(path_to_search), recursive=True)
    return paths


def get_suffix(file_path: str) -> str:
    # TODO: Deal with different forms of 'the same' file types consistently across all ingest modules.
    return pathlib.Path(file_path).suffix


def create_api_file_reference(
    file_path: str, study_uuid: str, dataset_uuid: str, crate_path: pathlib.Path
) -> list[APIModels.FileReference]:

    relative_path = pathlib.Path(file_path).relative_to(crate_path).as_posix()

    # TODO: Work out how file URI would be generated.

    file_reference = {
        "uuid": str(
            uuid_creation.create_file_reference_uuid(relative_path, study_uuid)
        ),
        "submission_dataset_uuid": dataset_uuid,
        "file_path": str(relative_path),
        "version": 0,
        "size_in_bytes": pathlib.Path(file_path).stat().st_size,
        "format": get_suffix(file_path),
        "uri": "None?",
    }

    return APIModels.FileReference(**file_reference)

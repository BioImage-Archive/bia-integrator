from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import pathlib
import glob
import logging
from typing import Optional

logger = logging.getLogger("__main__." + __name__)


def create_file_reference(
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
    crate_path: pathlib.Path,
    processed_file_paths: list[str],
) -> list[APIModels.FileReference]:
    ro_crate_datasets = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Dataset)
    )

    logger.warning(
        f"Creating file references but do not have a way to set the file URI yet. See TODO in {pathlib.Path(__file__)}."
    )

    file_reference_list = []
    for dataset in ro_crate_datasets:
        file_paths = find_files(dataset, crate_path)

        # TODO: deal with files not in datasets, and possibly edge cases like unzipped omezarrs, or nested datasets paths.

        dataset_uuid = str(uuid_creation.create_dataset_uuid(study_uuid, dataset.id))

        for file_path in file_paths:
            if pathlib.Path(file_path) not in processed_file_paths:
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
    file_path: str,
    study_uuid: str,
    dataset_uuid: str,
    crate_path: pathlib.Path,
    additional_attributes: Optional[list] = None,
) -> APIModels.FileReference:

    relative_path = pathlib.Path(file_path).relative_to(crate_path).as_posix()
    relative_path = pathlib.Path(file_path).relative_to(crate_path).as_posix()

    # TODO: Work out how file URI would be generated.

    file_size = pathlib.Path(file_path).stat().st_size

    uuid_string = f"{str(relative_path)} {file_size}"

    additional_metadata = []
    if additional_attributes and len(additional_attributes) > 0:
        additional_metadata.extend(additional_attributes)
    additional_metadata.append(
        AttributeModels.DocumentUUIDUinqueInputAttribute(
            provenance=APIModels.Provenance.BIA_INGEST,
            name="uuid_unique_input",
            value={"uuid_unique_input": uuid_string},
        ).model_dump()
    )

    file_reference = {
        "uuid": str(uuid_creation.create_file_reference_uuid(study_uuid, uuid_string)),
        "submission_dataset_uuid": dataset_uuid,
        "file_path": str(relative_path),
        "version": 0,
        "size_in_bytes": file_size,
        "format": get_suffix(file_path),
        "uri": "None?",
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": additional_metadata,
    }

    return APIModels.FileReference(**file_reference)

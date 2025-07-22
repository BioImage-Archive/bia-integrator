from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import pathlib
import glob
import logging
from typing import Optional
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
)
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_file_reference_uuid,
)

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

        dataset_uuid = str(create_dataset_uuid(study_uuid, dataset.id)[0])

        for file_path in file_paths:
            if pathlib.Path(file_path) not in processed_file_paths:
                file_reference_list.append(
                    create_api_file_reference(
                        {"http://bia/filePath": file_path},
                        study_uuid,
                        dataset_uuid,
                        crate_path,
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
    file_ref_dictionary: dict[str, str],
    study_uuid: str,
    dataset_uuid: str,
    crate_path: pathlib.Path,
    additional_attributes: Optional[list] = None,
) -> APIModels.FileReference:

    file_path = file_ref_dictionary["http://bia/filePath"]

    if pathlib.Path(file_path).is_absolute():
        relative_path = pathlib.Path(file_path).relative_to(crate_path).as_posix()
    else:
        relative_path = file_path

    # TODO: Work out how file URI would be generated.
    try:
        file_size = int(file_ref_dictionary["http://bia/sizeInBytes"])
    except KeyError:
        file_size = pathlib.Path(file_path).stat().st_size

    additional_metadata = []
    if additional_attributes and len(additional_attributes) > 0:
        additional_metadata.extend(additional_attributes)

    uuid, uuid_attribute = create_file_reference_uuid(
        study_uuid, str(relative_path), str(file_size)
    )
    additional_metadata.append(uuid_attribute.model_dump())

    file_reference = {
        "uuid": str(uuid),
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

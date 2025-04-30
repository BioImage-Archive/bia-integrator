from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import logging

logger = logging.getLogger("__main__." + __name__)


def create_api_dataset(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.Dataset]:
    ro_crate_datasets = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Dataset)
    )

    dataset_list = []
    for dataset in ro_crate_datasets:
        dataset_list.append(convert_dataset(dataset, study_uuid))

    return dataset_list


def convert_dataset(
    ro_crate_dataset: ROCrateModels.Dataset,
    study_uuid: str,
) -> APIModels.Dataset:

    title = None
    if ro_crate_dataset.title:
        title = ro_crate_dataset.title
    elif ro_crate_dataset.id:
        title = ro_crate_dataset.id

    dataset = {
        "uuid": str(uuid_creation.create_dataset_uuid(ro_crate_dataset.id, study_uuid)),
        "submitted_in_study_uuid": study_uuid,
        "title_id": title,
        "description": ro_crate_dataset.description,
        "version": 0,
        "example_image_uri": [],
    }

    return APIModels.Dataset(**dataset)

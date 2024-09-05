from typing import List, Type
from bia_shared_datamodels import bia_data_model
from bia_export.website_export.images.models import (
    ExperimentalImagingDataset,
)
from bia_export.website_export.datasets_for_images.retrieve import (
    retrieve_study,
    retrieve_datasets,
)
from bia_export.website_export.website_models import (
    CLIContext,
)


def transform_datasets(context: CLIContext) -> dict:
    dataset_map = {}
    api_study = retrieve_study(context)
    api_datasets = retrieve_datasets(context)
    for api_dataset in api_datasets:

        api_eid_dict = api_dataset.model_dump()
        api_eid_dict["submitted_in_study"] = api_study
        api_eid = ExperimentalImagingDataset(**api_eid_dict)
        dataset_map[str(api_eid.uuid)] = api_eid.model_dump(mode="json")

    return dataset_map

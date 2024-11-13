from bia_export.website_export.datasets_for_images.models import (
    Dataset,
)
from bia_export.website_export.datasets_for_images.retrieve import (
    retrieve_study,
    retrieve_datasets,
)
from bia_export.website_export.website_models import (
    CLIContext,
)


def transform_datasets(context: CLIContext) -> dict:
    # TODO: deal with ImageAnnotationDatasets for Derived Images
    dataset_map = {}
    api_study = retrieve_study(context)
    api_datasets = retrieve_datasets(context)
    for api_dataset in api_datasets:

        api_dataset_dict = api_dataset.model_dump()
        api_dataset_dict["submitted_in_study"] = api_study
        api_dataset = Dataset(**api_dataset_dict)
        dataset_map[str(api_dataset.uuid)] = api_dataset.model_dump(mode="json")

    return dataset_map

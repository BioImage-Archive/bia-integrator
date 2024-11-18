from bia_export.website_export.generic_object_retrieval import (
    read_all_json,
    read_api_json_file,
    get_source_directory,
    get_all_api_results,
)
from bia_export.website_export.website_models import CLIContext
from bia_export.bia_client import api_client
from bia_integrator_api import models as api_models

from typing import List
from glob import glob
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_datasets(
    context: CLIContext,
) -> List[api_models.Dataset]:
    if context.root_directory:
        api_datasets = read_all_json(object_type=api_models.Dataset, context=context)
    else:
        api_datasets = get_all_api_results(
            context.study_uuid, api_client.get_dataset_linking_study
        )

    return api_datasets


def retrieve_study(context: CLIContext) -> api_models.Study:
    if context.root_directory:
        study_directory = get_source_directory(api_models.Study, context)
        study_paths = glob(str(study_directory))

        if len(study_paths) != 1:
            raise Exception("Unexpected number of study objects")

        study_path = study_paths[0]

        study = read_api_json_file(study_path, api_models.Study)
    else:
        study = api_client.get_study(str(context.study_uuid))

    return study

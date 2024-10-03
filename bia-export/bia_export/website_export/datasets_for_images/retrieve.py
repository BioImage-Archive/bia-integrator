from bia_export.website_export.utils import (
    read_all_json,
    read_api_json_file,
    get_source_directory,
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
) -> List[api_models.ExperimentalImagingDataset]:
    if context.root_directory:

        api_datasets = read_all_json(
            object_type=api_models.ExperimentalImagingDataset, context=context
        )
    else:
        api_datasets = api_client.get_experimental_imaging_dataset_in_study(
            str(context.study_uuid)
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

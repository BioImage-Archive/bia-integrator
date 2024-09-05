from bia_export.website_export.utils import read_all_json, read_api_json_file
from bia_export.website_export.website_models import CLIContext
from bia_shared_datamodels import bia_data_model
from typing import List
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_datasets(
    context: CLIContext,
) -> List[bia_data_model.ExperimentalImagingDataset]:
    if context.root_directory:
        dataset_path = context.root_directory.joinpath(
            f"experimental_imaging_datasets/{context.accession_id}/*.json"
        )
        api_datasets = read_all_json(
            dataset_path, bia_data_model.ExperimentalImagingDataset
        )
    else:
        # TODO: impliment API client version
        raise NotImplementedError
    return api_datasets


def retrieve_study(context: CLIContext) -> bia_data_model.Study:
    if context.root_directory:
        study_path = context.root_directory.joinpath(
            f"studies/{context.accession_id}.json"
        )
        study = read_api_json_file(study_path, bia_data_model.Study)
    else:
        # TODO: impliment API client version
        raise NotImplementedError
    return study

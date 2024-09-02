from bia_export.website_export.datasets import (
    create_experimental_imaging_datasets,
)
from bia_export.website_export.utils import read_api_json_file
from .website_models import Study, StudyCreationContext
from bia_shared_datamodels import bia_data_model

import logging

logger = logging.getLogger("__main__." + __name__)


def create_study(context: StudyCreationContext) -> Study:

    api_study = retrieve_study(context)
    study_dict = api_study.model_dump()

    study_dict["experimental_imaging_component"] = create_experimental_imaging_datasets(
        context
    )

    study = Study(**study_dict)
    return study


def retrieve_study(context: StudyCreationContext) -> bia_data_model.Study:
    if context.root_directory:
        study_path = context.root_directory.joinpath(
            f"studies/{context.accession_id}.json"
        )

        logger.info(f"Loading study from {study_path}")

        api_study = read_api_json_file(study_path, bia_data_model.Study)
    else:
        # TODO: use client and context.study_uuid
        raise NotImplementedError

    return api_study

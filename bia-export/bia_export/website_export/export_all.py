from glob import glob
from pathlib import Path
from typing import Optional, Union
from bia_export.bia_client import api_client
from bia_export.website_export.studies.models import Study as exportStudy
from bia_integrator_api.models import Study as apiStudy
from .generic_object_retrieval import read_api_json_file
import logging
import re

logger = logging.getLogger("__main__." + __name__)


def find_local_studies(root_path: Path) -> list[apiStudy]:
    study_search_path = root_path.joinpath("study", "**/*.json")
    file_paths = glob(str(study_search_path), recursive=True)
    studies = []
    for file_path in file_paths:
        studies.append(read_api_json_file(file_path, apiStudy))
    return studies


def fetch_studies_from_api(
    page_size: int, agregator_list: list[apiStudy] = None
) -> list[apiStudy]:
    if not agregator_list:
        agregator_list = []
        start_uuid = None
    else:
        start_uuid = agregator_list[-1].uuid

    fetched_studies = api_client.search_study(
        page_size=page_size, start_from_uuid=start_uuid
    )
    agregator_list += fetched_studies

    if len(fetched_studies) != page_size:
        return agregator_list
    else:
        return fetch_studies_from_api(page_size, agregator_list)


def get_study_ids(root_directory: Optional[Path] = None):
    if root_directory:
        studies_list = find_local_studies(root_directory)
        sorted_studies = sort_studies(studies_list)
        return [study.accession_id for study in sorted_studies]
    else:
        studies_list = fetch_studies_from_api(page_size=100)
        sorted_studies = sort_studies(studies_list)
        return [study.uuid for study in sorted_studies]


def study_sort_key(study: Union[apiStudy, exportStudy, dict]) -> tuple[str, str]:
    def get_accno(acc_id):
        match = re.search(r"\d+$", acc_id)
        return int(match.group()) if match else None
    
    if isinstance(study, (apiStudy, exportStudy)):
        study = study.model_dump()
    
    return (study["release_date"], get_accno(study["accession_id"]))

def sort_studies(studies_list: list[Union[apiStudy, exportStudy]]):
    sorted_studies = sorted(
        studies_list,
        key=lambda study: study_sort_key(study),
        reverse=True,
    )

    return sorted_studies

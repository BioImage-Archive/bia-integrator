from glob import glob
from pathlib import Path
from typing import Optional, Union
from bia_export.bia_client import api_client
from bia_export.website_export.studies.models import Study as exportStudy
from bia_integrator_api.models import Study as apiStudy
from .generic_object_retrieval import (
    read_api_json_file,
)
import logging
import re
from json import dump, dumps
import gzip
from typing import Mapping, Any
from bia_export.website_export.website_models import CLIContext

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


def get_all_studies(root_directory: Optional[Path] = None):
    if root_directory:
        studies_list = find_local_studies(root_directory)
        sorted_studies = sort_studies(studies_list)
        return sorted_studies
    else:
        studies_list = fetch_studies_from_api(page_size=100)
        sorted_studies = sort_studies(studies_list)
        return sorted_studies


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


def extract_path(data, path):
    parts = path.split(".")

    def _extract(value, keys):
        if value is None:
            return None
        if not keys:
            return value

        key = keys[0]
        rest = keys[1:]
        if not isinstance(value, list) and not isinstance(value, dict):
            value = value.model_dump()
        if isinstance(value, list):
            out = []
            for item in value:
                v = _extract(item, keys)
                if v is None:
                    continue
                if isinstance(v, list):
                    out.extend(v)
                else:
                    out.append(v)
            return out or None

        if isinstance(value, dict):
            return _extract(value.get(key), rest)

        return None

    return _extract(data, parts)


def map_fields(source: dict, field_map: dict) -> dict:
    return {dest: extract_path(source, src) for src, dest in field_map.items()}


def transform_study_attr_to_dict(study_dict: dict, attr_field_map: dict) -> dict:
    study_attr_dict = {
        dest: extract_path(study_dict, src) for src, dest in attr_field_map.items()
    }
    return {
        key: list(dict.fromkeys(value)) if isinstance(value, list) else value
        for key, value in study_attr_dict.items()
    }


def write_json(path: Path, data: dict, description: str) -> None:
    logging.info(f"Writing {description} to {path.absolute()}")
    with open(path, "w") as output:
        dump(data, output)


def write_elastic_bulk_ndjson_gz(
    path: Path,
    documents: Mapping[str, dict[str, Any]],
    index_name: str,
    description: str,
    include_id: bool = True,
) -> None:
    logger.warning(f"Writing {description} to {path.absolute()}")

    with gzip.open(path, "wt", encoding="utf-8") as f:
        for doc_id, doc in documents.items():
            action = {"index": {"_index": index_name}}
            if include_id:
                action["index"]["_id"] = doc_id

            f.write(dumps(action, separators=(",", ":")))
            f.write("\n")
            f.write(dumps(doc, separators=(",", ":")))
            f.write("\n")


def write_elastic_bulk_ndjson_gz_chunks(
    output_prefix: Path,
    documents: Mapping[str, dict],
    index_name: str,
    description: str,
    docs_per_chunk: int = 2500,
) -> list[Path]:
    written_files: list[Path] = []
    items = list(documents.items())
    logger.warning(f"Writing {description} to {output_prefix.absolute()}")
    for chunk_num in range(0, len(items), docs_per_chunk):
        chunk = items[chunk_num : chunk_num + docs_per_chunk]
        path = (
            output_prefix.parent
            / f"{output_prefix.name}.part-{chunk_num // docs_per_chunk:05d}.ndjson.gz"
        )

        with gzip.open(path, "wt", encoding="utf-8") as f:
            for doc_id, doc in chunk:
                action = {"index": {"_index": index_name}}
                f.write(dumps(action, separators=(",", ":")) + "\n")
                f.write(dumps(doc, separators=(",", ":")) + "\n")

        written_files.append(path)

    return written_files

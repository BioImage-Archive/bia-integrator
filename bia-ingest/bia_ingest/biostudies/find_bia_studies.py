import requests
from bia_ingest.biostudies.api import SearchPage, SearchResult
import pathlib
from datetime import date
import logging
from typing import Optional
from bia_integrator_api.util import get_client
from bia_integrator_api.models import Study
from bia_ingest.settings import get_settings
import re

logger = logging.getLogger("__main__." + __name__)


def get_all_bia_studies(page_size: int) -> list[SearchResult]:
    BIOSTUDIES_COLLECTION_SEARCH = "https://www.ebi.ac.uk/biostudies/api/v1/BioImages/search?pageSize={page_size}&page={page_number}"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
    url = BIOSTUDIES_COLLECTION_SEARCH.format(page_size=1, page_number=1)
    total_hits = SearchPage.model_validate_json(
        requests.get(url, headers=headers).content
    ).totalHits

    results = []
    last_page = total_hits // page_size + 1
    page_count = 1

    while page_count <= last_page:

        url = BIOSTUDIES_COLLECTION_SEARCH.format(
            page_size=page_size, page_number=page_count
        )

        r = requests.get(url, headers=headers)
        assert r.status_code == 200
        search_page = SearchPage.model_validate_json(r.content)
        for hit in search_page.hits:
            results.append(hit)
        page_count += 1
    return results


def studies_by_source(
    list_of_search_results: list[SearchResult],
) -> dict[str, list[SearchResult]]:
    EMPIAR_studies = []
    BIAD_studies = []
    BSST_studies = []
    SJCBD_studies = []
    other_studies = []

    for result in list_of_search_results:
        accession_id: str = result.accession
        if accession_id.startswith("EMPIAR"):
            EMPIAR_studies.append(result)
        elif accession_id.startswith("S-BIAD"):
            BIAD_studies.append(result)
        elif accession_id.startswith("S-BSST"):
            BSST_studies.append(result)
        elif accession_id.startswith("S-JCBD"):
            SJCBD_studies.append(result)
        else:
            other_studies.append(result)

    return {
        "EMPIAR": EMPIAR_studies,
        "BIAD": BIAD_studies,
        "BSST": BSST_studies,
        "SJCBD": SJCBD_studies,
        "other": other_studies,
    }


def get_processed_studies() -> list[str]:
    # TODO: use BIA API to get all studies & update settings class to use env values for testing
    with open(
        pathlib.Path(__file__).parents[2] / "input_files" / "ingested_submissions", "r"
    ) as f:
        acc_ids = f.readlines()
    return [acc_id.strip("\n") for acc_id in acc_ids]


def fetch_studies_from_api(
    api_client, page_size: int, agregator_list: list[Study] = None
) -> list[Study]:
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
        return fetch_studies_from_api(api_client, page_size, agregator_list)


def find_unprocessed_studies(output_file: Optional[pathlib.Path]):
    def get_accno(acc_id):
        match = re.search(r"\d+$", acc_id)
        return int(match.group()) if match else None

    page_size = 100
    logging.info("Fetching all studies from biostudies")
    imaging_studies = get_all_bia_studies(page_size)
    grouped_studies = studies_by_source(imaging_studies)
    studies_of_interest = (
        grouped_studies["BIAD"] + grouped_studies["BSST"] + grouped_studies["other"]
    )
    acc_id_of_interest = [result.accession for result in studies_of_interest]
    logging.info("Fetching all studies from bia api")
    api_client = get_client(get_settings().bia_api_basepath)
    bia_existing_studies = fetch_studies_from_api(api_client, page_size)
    processed_acc_ids = [str(study.accession_id) for study in bia_existing_studies]
    unprocessed_acc_ids = sorted(list(set(acc_id_of_interest) - set(processed_acc_ids)), key=lambda acc_id : get_accno(acc_id))

    if not output_file:
        output_file = (
            pathlib.Path(__file__).parents[2]
            / "input_files"
            / f"uningested_studies_of_interest_{str(date.today())}"
        )

    logging.info(f"Writing uningested studies to: {output_file}")
    with open(output_file, "w") as f:
        for id in unprocessed_acc_ids:
            f.write(f"{id}\n")

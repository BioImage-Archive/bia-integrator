import requests
from bia_ingest.biostudies.api import SearchPage, SearchResult
import pathlib
from datetime import date
import logging
from typing import Optional

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
    with open(
        pathlib.Path(__file__).parents[2] / "input_files" / "ingested_submissions", "r"
    ) as f:
        acc_ids = f.readlines()
    return [acc_id.strip("\n") for acc_id in acc_ids]


def find_unprocessed_studies(output_file: Optional[pathlib.Path]):

    page_size = 100
    imaging_studies = get_all_bia_studies(page_size)
    grouped_studies = studies_by_source(imaging_studies)
    studies_of_interest = (
        grouped_studies["BIAD"] + grouped_studies["BSST"] + grouped_studies["other"]
    )
    acc_id_of_interest = [result.accession for result in studies_of_interest]
    processed_acc_ids = get_processed_studies()
    unprocessed_acc_ids = set(acc_id_of_interest) - set(processed_acc_ids)

    if not output_file:
        output_file = (
            pathlib.Path(__file__).parents[2]
            / "input_files"
            / f"uningested_studies_of_interest_{str(date.today())}"
        )

    with open(output_file, "w") as f:
        for id in unprocessed_acc_ids:
            f.write(f"{id}\n")

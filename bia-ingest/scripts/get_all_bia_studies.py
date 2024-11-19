import requests
from pydantic.json import pydantic_encoder
from pydantic import BaseModel
from typing import Optional, List
import json


class SearchResult(BaseModel):
    accession: str
    type: str
    title: str
    author: str
    links: int
    files: int
    release_date: str
    views: int
    isPublic: bool


class SearchPage(BaseModel):
    page: int
    pageSize: int
    totalHits: int
    isTotalHitsExact: bool
    sortBy: str
    sortOrder: str
    hits: List[SearchResult]
    query: Optional[str]
    facets: Optional[str]


BIOSTUDIES_COLLECTION_SEARCH = "https://www.ebi.ac.uk/biostudies/api/v1/BioImages/search?pageSize={page_size}&page={page_number}"


def get_all_bia_studies(page_size: int, total_hits: int):
    results = []
    last_page = total_hits // page_size + 1
    page_count = 1
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
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


# Get studies from BIOSTUDIES api and store them so we don't keep calling their API
if __name__ == "__main__":
    total_hits = 3048
    page_size = 100
    results = get_all_bia_studies(page_size, total_hits)

    with open("all_bia_studies_in_biostudies.json", "w") as f:
        f.write(json.dumps(results, default=pydantic_encoder))

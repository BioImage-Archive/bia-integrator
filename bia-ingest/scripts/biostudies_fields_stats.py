import logging
from rich import print
from rich.logging import RichHandler
from bia_ingest.biostudies.api import load_submission, Section
from pydantic import BaseModel, ValidationError
from typing import List, Optional
import json
import csv
import time

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)
logger = logging.getLogger()


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


def count_section_type(dict_to_edit: dict, section_to_count: str):
    if section_to_count not in dict_to_edit.keys():
        dict_to_edit[section_to_count] = 0
    dict_to_edit[section_to_count] += 1


def recurse_subsection(section: Section, dict_count: dict):
    count_section_type(dict_count, section.type)
    if len(section.subsections) > 0:
        for section in section.subsections:
            if type(section) is list:
                pass
            else:
                recurse_subsection(section, dict_count)


if __name__ == "__main__":
    with open("all_bia_studies_in_biostudies.json", "r") as f:
        result = json.load(f)

    EMPIAR_studies = []
    BIAD_studies = []
    BSST_studies = []
    SJCBD_studies = []
    other_studies = []

    for study in result:
        accession_id: str = study["accession"]
        if accession_id.startswith("EMPIAR"):
            EMPIAR_studies.append(study)
        elif accession_id.startswith("S-BIAD"):
            BIAD_studies.append(study)
        elif accession_id.startswith("S-BSST"):
            BSST_studies.append(study)
        elif accession_id.startswith("S-JCBD"):
            SJCBD_studies.append(study)
        else:
            other_studies.append(study)

    print(f"EMPIAR: {len(EMPIAR_studies)}")
    print(f"BIAD: {len(BIAD_studies)}")
    print(f"BSST: {len(BSST_studies)}")
    print(f"SJCBD: {len(SJCBD_studies)}")
    print(f"other: {len(other_studies)}")

    for study in other_studies:
        print(study["accession"])

    print("-----")

    target_studies = BIAD_studies + BSST_studies + other_studies

    count_rows = []
    bool_rows = []
    for study in target_studies:
        print(study["accession"])
        try:
            submission = load_submission(study["accession"])
        except AssertionError:
            time.sleep(0.25)
            try:
                submission = load_submission(study["accession"])
            except AssertionError:
                print(f"gave up on: {study['accession']} due to non 200 response")
                continue
        except ValidationError:
            print(f"gave up on: {study['accession']} due to validation error")
            continue
        count_section_types = {"accno": submission.accno}
        first_section = submission.section
        recurse_subsection(first_section, count_section_types)
        count_rows.append(count_section_types)
        bool_section_types = {"accno": submission.accno}
        for key, count in count_section_types.items():
            if not key == "accno":
                if count > 0:
                    bool_section_types[key] = 1
                else:
                    bool_section_types[key] = 0
        bool_rows.append(bool_section_types)

    field_names = []
    for row in count_rows:
        for key in row.keys():
            if key not in field_names:
                field_names.append(key)

    with open("biad_field_counts.csv", "w") as f:
        wr = csv.DictWriter(f, field_names)
        wr.writeheader()
        for row in count_rows:
            wr.writerow(row)

    with open("biad_field_presence.csv", "w") as f:
        wr = csv.DictWriter(f, field_names)
        wr.writeheader()
        for row in bool_rows:
            wr.writerow(row)

import logging
import pathlib
from typing import Union, Optional

import requests
from pydantic import BaseModel, ConfigDict
from ro_crate_ingest.settings import get_settings


logger = logging.getLogger("__main__." + __name__)


STUDY_URL_TEMPLATE = "https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}"
STUDY_TABLE_INFO_URL_TEMPLATE = (
    "https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}/info"
)
FLIST_URI_TEMPLATE = (
    "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{flist_fname}"
)
FILE_URI_TEMPLATE = "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{relpath}"


class AttributeDetail(BaseModel):
    name: str
    value: str


class Attribute(BaseModel):
    name: str
    value: Optional[str] = None
    reference: bool = False
    nmqual: list[AttributeDetail] = []
    valqual: list[AttributeDetail] = []


# File list


class File(BaseModel):
    path: pathlib.Path
    size: int
    type: str
    attributes: list[Attribute] = []


class Link(BaseModel):
    url: Optional[str] = None
    attributes: list[Attribute] = []


class Empty(BaseModel):
    """
    A class for empty objects, i.e. { } in a json document, that can come up in biostudies responses (e.g. some submission links).
    """

    model_config = ConfigDict(extra="forbid")


class Section(BaseModel):
    type: str
    accno: Optional[str] = ""
    attributes: list[Attribute] = []
    subsections: list[Union["Section", list["Section"]]] = []
    links: list[Union[Link, list[Link], Empty]] = []
    files: list[Union[File, list[File]]] = []


class Submission(BaseModel):
    accno: Optional[str] = ""
    section: Section
    attributes: list[Attribute]
    files: Optional[list] = []


def load_submission(accession_id: str) -> Submission:
    # Note this is a dictionary to include reasons why the override was made
    overrides = {
        "S-BIADTEST_AUTHOR_AFFILIATION": "A test submission that covers different author and affiliations options."
    }
    if accession_id in overrides:
        return read_override(accession_id)
    else:
        return submission_from_biostudies_api(accession_id)


def read_override(accession_id: str) -> Submission:

    submission_path = pathlib.Path(
        get_settings().biostudies_override_dir,
        accession_id,
        f"{accession_id}_override.json",
    )
    abs_path = submission_path.absolute()
    logger.info(f"Reading submission from {abs_path}")
    file = abs_path.read_text()
    submission = Submission.model_validate_json(file)
    assert submission.accno == accession_id
    return submission


def submission_from_biostudies_api(accession_id) -> Submission:
    url = STUDY_URL_TEMPLATE.format(accession=accession_id)
    logger.info(f"Fetching submission from {url}")
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
    r = requests.get(url, headers=headers)

    assert r.status_code == 200

    # As of 21/05/2025, biostudies UI may return either pagetab json or a forwarding url
    # see: https://biostudies.slack.com/archives/CH32H9SSK/p1747738324948869?thread_ts=1747736444.671019&cid=CH32H9SSK
    if "ftpHttp_link" in r.json():
        forward_to_url = f"{r.json().get('ftpHttp_link')}{accession_id}.json"
        r = requests.get(forward_to_url, headers=headers)
        assert r.status_code == 200

    submission = Submission.model_validate_json(r.content)

    return submission

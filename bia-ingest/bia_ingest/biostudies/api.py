import json
import logging
import pathlib
import datetime
from typing import List, Union, Dict, Optional, Any
from copy import deepcopy

import requests
from pydantic import BaseModel, TypeAdapter, ConfigDict


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
    nmqual: List[AttributeDetail] = []
    valqual: List[AttributeDetail] = []

    def as_tsv(self) -> str:
        if self.reference:
            tsv_rep = f"<{self.name}>\t{self.value}\n"
        else:
            tsv_rep = f"{self.name}\t{self.value}\n"

        return tsv_rep


# File List


class File(BaseModel):
    path: pathlib.Path
    size: int
    type: str
    attributes: List[Attribute] = []


class Link(BaseModel):
    url: Optional[str] = None
    attributes: List[Attribute] = []

    def as_tsv(self) -> str:
        tsv_rep = "\n"
        tsv_rep += f"Link\t{self.url}\n"
        tsv_rep += "".join([attr.as_tsv() for attr in self.attributes])

        return tsv_rep


class Empty(BaseModel):
    """
    A class for empty objects, i.e. { } in a json document, that can come up in biostudies responses (e.g. some submission links).
    """

    model_config = ConfigDict(extra="forbid")


class Section(BaseModel):
    type: str
    accno: Optional[str] = ""
    attributes: List[Attribute] = []
    subsections: List[Union["Section", List["Section"]]] = []
    links: List[Union[Link, List[Link], Empty]] = []
    files: List[Union[File, List[File]]] = []

    def as_tsv(self, parent_accno: Optional[str] = None) -> str:
        tsv_rep = "\n"

        accno_str = self.accno if self.accno else ""
        if parent_accno:
            tsv_rep += f"{self.type}\t{accno_str}\t{parent_accno}"
        else:
            if self.accno:
                tsv_rep += f"{self.type}\t{accno_str}"
            else:
                tsv_rep += f"{self.type}"

        tsv_rep += "\n"

        tsv_rep += "".join([attr.as_tsv() for attr in self.attributes])
        tsv_rep += "".join([link.as_tsv() for link in self.links])
        tsv_rep += "".join([section.as_tsv(self.accno) for section in self.subsections])

        return tsv_rep


class Submission(BaseModel):
    accno: Optional[str] = ""
    section: Section
    attributes: List[Attribute]
    files: Optional[list] = []

    def as_tsv(self) -> str:
        tsv_rep = "Submission"
        if self.accno:
            tsv_rep += f"\t{self.accno}"
        tsv_rep += "\n"

        tsv_rep += "".join([attr.as_tsv() for attr in self.attributes])
        tsv_rep += self.section.as_tsv()

        return tsv_rep


# API search classes


class StudyResult(BaseModel):
    accession: str
    title: str
    author: str
    links: int
    files: int
    release_date: datetime.date
    views: int
    isPublic: bool


class QueryResult(BaseModel):
    page: int
    pageSize: int
    totalHits: int
    isTotalHitsExact: bool
    sortBy: str
    sortOrder: str
    hits: List[StudyResult]


# API table structure


class Columns(BaseModel):
    name: str
    title: str
    visible: bool
    searchable: bool
    data: Optional[str] = None
    sortable: Optional[bool] = True
    defaultContent: str


class SubmissionTable(BaseModel):
    columns: List[Columns]
    files: int
    httpLink: str
    ftpLink: str
    globusLink: str
    isPublic: bool
    relPath: str
    hasZippedFolders: bool
    views: int
    released: int
    modified: int
    sections: Optional[List[str]] = None


# Search data structures


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


# API functions


def load_submission_table_info(accession_id: str) -> SubmissionTable:
    url = STUDY_TABLE_INFO_URL_TEMPLATE.format(accession=accession_id)
    logger.debug(f"Fetching table information from {url}")
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    assert r.status_code == 200
    table_info = SubmissionTable.model_validate_json(r.content)
    return table_info


def load_submission(accession_id: str) -> Submission:
    # Note this is a dictionary to include reasons why the override was made
    overrides = {
        "S-BSMS4": "Author links to affiliations were missing 'reference: true'",
        "S-BIAD15": "Invalid licence, and affilicaiton was missing accno",
        "S-BIAD1076": "Biosample had the Experimental variables text split up into 3 sections, possibly due to commas?",
        "S-BIAD1261": "Author had no name, and the email was for a whole lab. Name added as Cytology Department RUB",
        "S-BIAD978": "Unreferenced Image analysis-5, and a broken association to image analysis 1 (that doesn't exist)",
        "S-BIAD954": "invalid email: Julia Nöth <julia.noeth@ufz.de> changed to: julia.noeth@ufz.de",
        "S-BIAD1136": "invalid email: oona.paavolainen@ut changed to: oona.k.paavolainen@utu.fi (same ending as other authors - seemed to be missing the .k. based off google search)",
        "S-BIAD1223": "invalid email: ylva.ivarsson@kemi..u.se changed to: ylva.ivarsson@kemi.uu.se",
        "S-BIAD1344": "invalid email: raffaeledefilippis92@gmail.comraffaeledefilippis92@gmail.com changed to: raffaeledefilippis92@gmail.com",
        "S-BSST651": "invalid email: huw.williams@williams@nottingham.ac.uk changed to: huw.williams@nottingham.ac.uk",
        "S-BSST744": "invalid email: ‫britta.engelhardt@tki.unibe.ch (right-to-left embedding) changed to: britta.engelhardt@tki.unibe.ch",
        "S-BIAD590": "missing study component assosiations subsection",
        "S-BIAD599": "missing study component assosiations subsection",
        "S-BIAD628": "missing study component assosiations subsection",
        "S-BIAD677": "missing study component assosiations subsection",
        "S-BIAD2250": "Dataset cannot find Specimen Imaging Prepration Protocol that exists in its associations: All specimens",
    }
    if accession_id in overrides:
        return read_override(accession_id)
    else:
        return submission_from_biostudies_api(accession_id)


def read_override(accession_id: str) -> Submission:
    submission_path = pathlib.Path(
        "submission_overrides/biostudies", accession_id, f"{accession_id}_override.json"
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


def file_uri(
    accession_id: str, file: File, file_uri_template: Optional[str] = FILE_URI_TEMPLATE
) -> str:
    """For a given accession and file object, return the HTTP URI where we can expect
    to be able to access that file."""

    return file_uri_template.format(
        accession_id=accession_id, relpath=file.path.as_posix()
    )


def get_file_uri_template_for_accession(accession_id: str) -> str:
    """Given an accession identifier, use the BioStudies API to generate a
    template which can be populated with the value of relpath to produce
    the URI for a given file."""

    request_uri = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession_id}/info"
    r = requests.get(request_uri)
    raw_obj = json.loads(r.content)
    # Strip the initial ftp from the ftp link, replace by http and add /Files
    accession_base_uri = "https" + raw_obj["ftpLink"][3:] + "/Files"

    file_uri_template = accession_base_uri + "/{relpath}"

    return file_uri_template


def get_with_case_insensitive_key(dictionary: Dict[str, Any], key: str) -> Any:
    keys = [k.lower() for k in dictionary.keys()]
    temp_key = key.lower()
    if temp_key in keys:
        key_index = keys.index(temp_key)
        temp_key = list(dictionary.keys())[key_index]
        return dictionary[temp_key]
    else:
        raise KeyError(f"{key} not in {dictionary.keys()}")


def filter_filelist_content(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove attributes in filelist with null or empty values
    """
    dict_copy = deepcopy(dictionary)
    for d in dict_copy:
        if "attributes" in d:
            d["attributes"] = [
                i
                for i in filter(
                    lambda x: x != {"value": "null"} and x != {}, d["attributes"]
                )
            ]
            if len(d["attributes"]) == 0:
                d.pop("attributes")

    return dict_copy


def flist_from_flist_fname(
    accession_id: str, flist_fname: str, extra_attribute: Union[List[str], str] = None
) -> List[File]:
    flist_url = FLIST_URI_TEMPLATE.format(
        accession_id=accession_id, flist_fname=flist_fname
    )

    r = requests.get(flist_url)
    logger.info(f"Fetching file list from {flist_url}")
    assert r.status_code == 200

    # fl = parse_raw_as(List[File], r.content)
    # KB 18/08/2023 - Hack to fix error due to null values in attributes
    # Remove attribute entries with {"value": "null"}
    dict_content = json.loads(r.content)
    dict_filtered_content = filter_filelist_content(dict_content)
    filtered_content = bytes(json.dumps(dict_filtered_content), "utf-8")
    fl = TypeAdapter(List[File]).validate_json(filtered_content)

    if extra_attribute:
        if not isinstance(extra_attribute, list):
            extra_attribute = [
                extra_attribute,
            ]
        for file in fl:
            file.attributes.extend(extra_attribute)

    return fl

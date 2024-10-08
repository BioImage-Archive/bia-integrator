import json
import logging
import pathlib
import datetime
from typing import List, Union, Dict, Optional, Any
from copy import deepcopy

import requests
from pydantic import BaseModel, TypeAdapter


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
    url: str
    attributes: List[Attribute] = []

    def as_tsv(self) -> str:
        tsv_rep = "\n"
        tsv_rep += f"Link\t{self.url}\n"
        tsv_rep += "".join([attr.as_tsv() for attr in self.attributes])

        return tsv_rep


class Section(BaseModel):
    type: str
    accno: Optional[str] = ""
    attributes: List[Attribute] = []
    subsections: List[Union["Section", List["Section"]]] = []
    links: List[Link] = []
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
    accno: Optional[str]
    section: Section
    attributes: List[Attribute]

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
    data: str
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
    sections: List[str]


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
    url = STUDY_URL_TEMPLATE.format(accession=accession_id)
    logger.info(f"Fetching submission from {url}")
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
    r = requests.get(url, headers=headers)

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

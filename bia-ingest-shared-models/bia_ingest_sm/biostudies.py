import json
import logging
import pathlib
import datetime
from typing import List, Union, Dict, Optional, Any
from copy import deepcopy

import requests
from pydantic import BaseModel


logger = logging.getLogger(__name__)


STUDY_URL_TEMPLATE = "https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}"
FLIST_URI_TEMPLATE = (
    "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{flist_fname}"
)
FILE_URI_TEMPLATE = "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{relpath}"


class AttributeDetail(BaseModel):
    name: str
    value: str


class Attribute(BaseModel):
    name: str
    value: Optional[str]
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
        tsv_rep = f"Submission"
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


# API functions


def load_submission(accession_id: str) -> Submission:

    url = STUDY_URL_TEMPLATE.format(accession=accession_id)
    logger.info(f"Fetching submission from {url}")
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
    r = requests.get(url, headers=headers)

    assert r.status_code == 200

    submission = Submission.parse_raw(r.content)

    return submission


def attributes_to_dict(attributes: List[Attribute]) -> Dict[str, Optional[str]]:

    return {attr.name: attr.value for attr in attributes}


def find_file_lists_in_section(
    section: Section, flists: List[Dict[str, Union[str, None, List[str]]]]
) -> List[Dict[str, Union[str, None, List[str]]]]:
    """Find all of the File Lists in a Section, recursively descending through
    the subsections.
    
    Return a list of dictionaries.
    """

    attr_dict = attributes_to_dict(section.attributes)

    if "File List" in attr_dict:
        flists.append(attr_dict)
        # Get details of any associations in this subsection
        attr_dict["associations"] = []
        for subsection in section.subsections:
            if subsection.type == "Associations":
                attr_dict["associations"].append(
                    attributes_to_dict(subsection.attributes)
                )

    for subsection in section.subsections:
        subsection_type = type(subsection)
        if subsection_type == Section:
            find_file_lists_in_section(subsection, flists)
        else:
            logger.warning(
                f"Not processing subsection as type is {subsection_type}, not 'Section'. Contents={subsection}"
            )

    return flists


def find_file_lists_in_submission(
    submission: Submission,
) -> List[Dict[str, Union[str, None, List[str]]]]:

    return find_file_lists_in_section(submission.section, [])


# KB 14/06/2024 commented out as I need to replace parse_raw_as with 
# TypeAdapter for pydantic >=2
#def flist_from_flist_fname(
#    accession_id: str, flist_fname: str, extra_attribute: Union[List[str], str] = None
#) -> List[File]:
#
#    flist_url = FLIST_URI_TEMPLATE.format(
#        accession_id=accession_id, flist_fname=flist_fname
#    )
#
#    r = requests.get(flist_url)
#    logger.info(f"Fetching file list from {flist_url}")
#    assert r.status_code == 200
#
#    # fl = parse_raw_as(List[File], r.content)
#    # KB 18/08/2023 - Hack to fix error due to null values in attributes
#    # Remove attribute entries with {"value": "null"}
#    dict_content = json.loads(r.content)
#    dict_filtered_content = filter_filelist_content(dict_content)
#    filtered_content = bytes(json.dumps(dict_filtered_content), "utf-8")
#    fl = parse_raw_as(List[File], filtered_content)
#
#    if extra_attribute:
#        if type(extra_attribute) is not list:
#            extra_attribute = [
#                extra_attribute,
#            ]
#        for file in fl:
#            file.attributes.extend(extra_attribute)
#
#    return fl


def file_uri(
    accession_id: str, file: File, file_uri_template: Optional[str] = FILE_URI_TEMPLATE
) -> str:
    """For a given accession and file object, return the HTTP URI where we can expect
    to be able to access that file."""

    return file_uri_template.format(accession_id=accession_id, relpath=file.path)


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


def find_files_in_submission_file_lists(submission: Submission) -> List[File]:

    file_list_dicts = find_file_lists_in_submission(submission)
    file_lists = []
    for file_list_dict in file_list_dicts:
        fname = file_list_dict["File List"]
        extra_attribute = []
        if "Title" in file_list_dict:
            extra_attribute.append(
                Attribute(name="Title", value=file_list_dict["Title"])
            )
        if "associations" in file_list_dict:
            extra_attribute.append(
                Attribute(
                    name="associations", value=f"{file_list_dict['associations']}"
                )
            )
        file_list = flist_from_flist_fname(submission.accno, fname, extra_attribute)
        file_lists.append(file_list)

    return sum(file_lists, [])


def find_files_in_submission(submission: Submission) -> List[File]:
    """Find all of the files in a submission, both attached directly to
    the submission and as file lists."""

    all_files = find_files_in_submission_file_lists(submission)

    def descend_and_find_files(section, files_list=[]):

        section_type = type(section)
        if section_type == Section:
            for file in section.files:
                if isinstance(file, List):
                    files_list += file
                else:
                    files_list.append(file)

            for subsection in section.subsections:
                descend_and_find_files(subsection, files_list)
        else:
            logger.warning(
                f"Not processing subsection as type is {section_type}, not 'Section'. Contents={section}"
            )

    descend_and_find_files(submission.section, all_files)

    return all_files


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
    """Remove attributes in filelist with null or empty values

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

import json
import requests
from pydantic import TypeAdapter, BaseModel
from typing import Any
import pathlib
from .submission_api import Attribute
import logging
from ro_crate_ingest.settings import get_settings


logger = logging.getLogger("__main__." + __name__)

FLIST_URI_TEMPLATE = (
    "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{flist_fname}"
)


# File list


class File(BaseModel):
    path: pathlib.Path
    size: int
    type: str
    attributes: list[Attribute] = []


def filter_filelist_content(
    list_of_fref_dictionaries: list[dict[str, Any]],
) -> None:
    """
    Remove attributes in filelist with null or empty values
    """
    for fref in list_of_fref_dictionaries:
        if "attributes" in fref:
            fref["attributes"] = [
                i
                for i in filter(
                    lambda x: x != {"value": "null"} and x != {}, fref["attributes"]
                )
            ]
            if len(fref["attributes"]) == 0:
                fref.pop("attributes")


def load_filelist(accession_id: str, flist_fname: str):
    # Note, this is not necessarily the same override list as the load_submission in submission_api.py
    overrides = {
        "S-BIADTEST_AUTHOR_AFFILIATION": "A test submission that covers different author and affiliations options.",
        "S-BIADTEST_COMPLEX_BIOSAMPLE": "A test submission that covers different biosample, taxon, and REMBI study component associations.",
        "S-BIAD843": "For testing.",
    }
    if accession_id in overrides:
        return read_override(accession_id, flist_fname)
    else:
        return file_list_from_biostudies_api(accession_id, flist_fname)


def read_override(accession_id, flist_fname) -> list[File]:
    submission_path = pathlib.Path(
        get_settings().biostudies_override_dir, accession_id, flist_fname
    )
    abs_path = submission_path.absolute()
    logger.info(f"Reading filelist from from {abs_path}")
    file = abs_path.read_text()

    dict_content = json.loads(file)
    filter_filelist_content(dict_content)
    filtered_content = bytes(json.dumps(dict_content), "utf-8")
    fl = TypeAdapter(list[File]).validate_json(filtered_content)
    return fl


def file_list_from_biostudies_api(accession_id: str, flist_fname: str) -> list[File]:
    flist_url = FLIST_URI_TEMPLATE.format(
        accession_id=accession_id, flist_fname=flist_fname
    )

    r = requests.get(flist_url)
    logger.info(f"Fetching file list from {flist_url}")
    assert r.status_code == 200

    dict_content = json.loads(r.content)
    filter_filelist_content(dict_content)
    filtered_content = bytes(json.dumps(dict_content), "utf-8")
    fl = TypeAdapter(list[File]).validate_json(filtered_content)

    return fl

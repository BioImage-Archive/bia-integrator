import logging
import requests
import json
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Entry
from ro_crate_ingest.settings import get_settings
import pathlib

logger = logging.getLogger("__main__." + __name__)


def load_empiar_entry(accession_id) -> Entry:
    # Note this is a dictionary to include reasons why the override was made
    overrides = {
        "EMPIAR-IMAGEPATTERNTEST": "A test submission covering file pattern shapes.",
        "EMPIAR-STARFILETEST": "A test submission covering star file annotation, with tomograms, and other image dependencies.",
        "EMPIAR-IMAGELABELTEST": "A test submission covering file-to-image grouping strategies."
    }
    if accession_id in overrides:
        return read_empiar_entry_override(accession_id)
    else:
        return empiar_entry_from_accession_id(accession_id)


def empiar_entry_from_accession_id(accession_id: str) -> Entry:
    accession_no = accession_id.split("-")[1]
    logger.info(f"Generating study for EMPIAR entry {accession_no}")
    empiar_uri = f"https://www.ebi.ac.uk/empiar/api/entry/{accession_no}"

    r = requests.get(empiar_uri)
    raw_data = json.loads(r.content)

    accession_obj = raw_data[accession_id]
    entry = Entry(**accession_obj)

    return entry


def read_empiar_entry_override(accession_id) -> Entry:
    accession_no = accession_id.split("-")[1]

    submission_path = pathlib.Path(
        get_settings().empiar_override_dir,
        accession_id,
        f"{accession_no}.json",
    )
    abs_path = submission_path.absolute()
    logger.info(f"Reading submission from {abs_path}")
    file = json.loads(abs_path.read_text())
    entry_dict = file[accession_id]
    entry = Entry(**entry_dict)
    return entry

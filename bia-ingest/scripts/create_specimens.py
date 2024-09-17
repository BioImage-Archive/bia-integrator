"""Create specific objects and persist to API"""

import sys
from bia_ingest.config import api_client
from bia_ingest.serialiser import MongodbSerialiser
from bia_ingest.conversion import specimen, experimental_imaging_dataset
from bia_ingest.biostudies import load_submission
from bia_ingest.cli_logging import IngestionResult

mongodb_serialiser = MongodbSerialiser(api_client)


def create_and_persist_specimens(accession_id):
    result_summary = {accession_id: IngestionResult()}
    submission = load_submission(accession_id)
    specimens = specimen.get_specimen(submission, result_summary)
    mongodb_serialiser.serialise(specimens)

    eid = experimental_imaging_dataset.get_experimental_imaging_dataset(
        submission, result_summary
    )
    mongodb_serialiser.serialise(eid)

    print(result_summary)


# From https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


if __name__ == "__main__":
    accession_id = sys.argv[1]
    create_and_persist_specimens(accession_id)

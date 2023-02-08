import logging
import datetime

import click
import pandas as pd
from bia_integrator_core.interface import (
    get_all_study_identifiers
)
from bia_integrator_core.integrator import (
    load_and_annotate_study
)

from bia_integrator_tools.utils import get_ome_ngff_rep


COLUMNS = [
    "OME-NGFF version",
    "EMBL-EBI bucket (current)",
    "SizeX",
    "SizeY",
    "SizeZ",
    "SizeC",
    "SizeT",
    "Axes",
    "Wells",
    "Fields",
    "Keywords",
    "License",
    "Study",
    "DOI",
    "Date added",
    "Representative Image ID",
    "Size (bytes)"
]


def image_to_catalogue_entry(image):
    ome_ngff_rep = get_ome_ngff_rep(image)

    selected_keys = [
        "SizeX",
        "SizeY",
        "SizeZ",
        "SizeC",
        "SizeT"
    ]

    fixed = {
        "OME-NGFF version": 0.4,
        "Axes": "XYZCT",
        "Wells": None,
        "Fields": None,
        "DOI": None,
        "License": "CC0",
        "Keywords": None
    }

    other = {
        "Study": ome_ngff_rep.accession_id,
        "EMBL-EBI bucket (current)": ome_ngff_rep.uri,
        "Date added": datetime.date.today(),
        "Representative Image ID": None,
        "Size (bytes)": ome_ngff_rep.size

    }

    entry = {key: image.attributes[key] for key in selected_keys}
    entry.update(fixed)
    entry.update(other)

    return entry



@click.command()
def main():
    logging.basicConfig(level=logging.INFO)

    accession_ids = get_all_study_identifiers()

    entries = []

    for accession_id in accession_ids:
        study = load_and_annotate_study(accession_id)

        for image in study.images.values():
            ome_ngff_rep = get_ome_ngff_rep(image)

            if ome_ngff_rep:
                try:
                    entry = image_to_catalogue_entry(image)
                    entries.append(entry)
                except KeyError as e:
                    logging.info(f"Can't find {e} for {accession_id}:{image.id}")
                    pass

    # print(entries)

    df = pd.DataFrame(entries, columns=COLUMNS)

    print(df.to_csv(index=False))



if __name__ == "__main__":
    main()
import sys
from pathlib import Path
import logging
import io
import csv
import json
import ast

import click

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.cli import sizeof_fmt
from bia_integrator_core.models import StudyAnnotation
from bia_integrator_core.interface import persist_study_annotation

logger = logging.getLogger(__file__)

def save_dict_to_tsv(dictionary, filename):
    with open(filename, "w", newline="") as tsv_file:
        writer = csv.writer(
            tsv_file,
            delimiter="\t",
            lineterminator="\n"
        )
        writer.writerow(dictionary.keys())  # Write the column headers
        rows = zip(*dictionary.values())   # Transpose the values
        writer.writerows(rows)             # Write the rows

def dict_to_tsv(dictionary, output):
    writer = csv.writer(output, delimiter="\t")
    writer.writerow(dictionary.keys())  # Write the column headers
    rows = zip(*dictionary.values())   # Transpose the values
    writer.writerows(rows)             # Write the rows
    return output

def _initialise_list(length, value=""):
    return [ value for i in range(length) ]

def combine_study_filetype_info(accession_ids: list) -> list:
    """Present filetype info for each study in a single tab separated row

    """

    n_studies = len(accession_ids)

    # Initialise output dict
    dict_summary = {
        "accession_id": _initialise_list(n_studies),
        "release_date": _initialise_list(n_studies),
        "title": _initialise_list(n_studies),
        "n_files_excluding_zip_contents": _initialise_list(n_studies, 0),
        "n_files_including_zip_contents": _initialise_list(n_studies, 0),
        "study_size_in_bytes": _initialise_list(n_studies, 0),
        "study_size_human_readable": _initialise_list(n_studies),
    }

    for i, accession_id in enumerate(accession_ids):
        try:
            bia_study = load_and_annotate_study(accession_id)
        except FileNotFoundError as e:
            dict_summary["accession_id"][i] = f"{accession_id}.json not found."
            logger.error(f"{e}\nHave you run 'ingest_from_biostudies.py and summarise_study_filetypes.py on this study?")
            continue
        dict_summary["accession_id"][i] = accession_id
        dict_summary["release_date"][i] = bia_study.release_date
        dict_summary["title"][i] = bia_study.title

        attribute_keys = [
            "n_files_excluding_zip_contents",
            "n_files_including_zip_contents",
            "study_size_in_bytes",
            "study_size_human_readable",
            ]
        for attribute_key in attribute_keys:
            try:
                dict_summary[attribute_key][i] = bia_study.attributes[attribute_key]
            except KeyError as e:
                logger.error(f"Error processing {accession_id}. {e}")
                continue
            
        filetype_breakdown = ast.literal_eval(bia_study.attributes["filetype_breakdown"])
        for filetype, filetype_stats in filetype_breakdown.items():
            for filetype_stat_key, filetype_stat_value in filetype_stats.items():
                col_name = f"{filetype}:{filetype_stat_key}"
                if col_name not in dict_summary.keys():
                    dict_summary[col_name] = _initialise_list(n_studies, "0")
                dict_summary[col_name][i] = str(filetype_stat_value)
                
    return dict_summary
#
#    summary = io.StringIO()
#    writer = csv.writer(
#        summary,
#        delimiter="\t",
#        lineterminator="\n"
#    )
#    writer.writerow(dict_summary.keys())
#    rows = zip(*dict_summary.values())   # Transpose the values
#    writer.writerows(rows)             # Write the rows
#
#    return summary.getvalue()

@click.command()
@click.option('--accession-ids', help='Comma separated accession_ids e.g. S-BIAD1,S-BIAD3')
@click.option('--accession-ids-path', help='Path to text file containing accession ids to process')
@click.option("--output-path", help="Path to save summary tsv file")
def main(accession_ids: str, accession_ids_path, output_path) -> None:
    """Create tsv of filetype info for input studies

    Create a tsv containing the contents of filetype information for the
    accession_ids submitted. These can be a comma separated list of ids
    or the path to a file containing accession ids

    It is assumed that ingest_from_biostudies.py and 
    summarise_study_filetypes.py have been run on each study.
    """
    
    logging.basicConfig(level=logging.INFO)

    if accession_ids is not None:
        accession_ids = accession_ids.split(",")
    else:
        accession_ids = []

    if accession_ids_path is not None:
        accession_ids.extend([line for line in Path(accession_ids_path).read_text().split("\n") if len(line) > 0])

    if len(accession_ids) == 0:
        click.echo("Please specify exactly one parameter.")
        return

    dict_summary = combine_study_filetype_info(accession_ids)
    
    if output_path is None:
        temp_dir = Path("./tmp")
        if not temp_dir.is_dir():
            temp_dir.mkdir()
        output_path = str(temp_dir / "study_filetype_info.tsv")

    save_dict_to_tsv(dict_summary, output_path)
    logger.info(f"Saved summary to {output_path}")

if __name__ == "__main__":
    main()

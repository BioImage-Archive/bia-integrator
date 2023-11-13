"""Script and helper functions to save annotations of filetype info

The main function saves annotations of information about the types of files
in the study referenced by the accession_id supplied. This includes the
content of zip files.
"""

import sys
from pathlib import Path
import logging

import click

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.cli import sizeof_fmt
from bia_integrator_api.models import StudyAnnotation, FileReference
from bia_integrator_core.interface import persist_study_annotation
from bia_integrator_core.config import settings

logger = logging.getLogger(__file__)

def _get_extension(p):
    """Return the standardized file extension for a given file path."""

    special_cases = {
        ".ome.zarr.zip": ".ome.zarr.zip",
        ".zarr.zip": ".zarr.zip",
        ".ome.zarr": ".ome.zarr",
        ".ome.tiff": ".ome.tiff",
        ".ome.tif" : ".ome.tiff",
        ".tar.gz": ".tar.gz",
    }

    for special_ext, mapped_value in special_cases.items():
        if p.lower().endswith(special_ext):
            return mapped_value
    
    ext_map = {
        ".jpeg": ".jpg",
        ".tiff": ".tif",
    }
    ext = Path(p).suffix.lower()
    if ext in ext_map:
        return ext_map[ext]
    else:
        return ext


def summarise_fileref_filetypes(filerefs: list[FileReference]) -> dict:
    """Return number of files of each type and sum of their sizes

    Return a dict with filetype extension as keys and a dict of
    info for each filetype:
        - number of files
        - total size in bytes
        - formatted total size
    """

    ftypes = {}

    for f in filerefs:
        ext = _get_extension(f.name)
        uri_ext = _get_extension(f.uri)
        if f.size_in_bytes == 0:
            continue
        if len(ext) == 0:
            ext = "none"
        if  f.type == "directory":
            ext = uri_ext
        elif f.type == "file_in_zip":
            ext = f"{ext} in {uri_ext}"
        if ext in ftypes:
            ftypes[ext]["n"] = ftypes[ext]["n"] + 1
            ftypes[ext]["size_in_bytes"] = ftypes[ext]["size_in_bytes"] + f.size_in_bytes
        else:
            ftypes[ext] = {"n": 1, "size_in_bytes": f.size_in_bytes}

    # Create human readable sizes with appropriate units
    for ftype, details in ftypes.items():
        ftypes[ftype]["size_human_readable"] = sizeof_fmt(details["size_in_bytes"])

    return ftypes

def filetypes_as_html(ftypes: dict) -> str:
    """Convert values of each file type to html - display as list

    """
    html = ""
    zip_html = ""
    for k in sorted(ftypes):
        line = f"<li>{k}: {ftypes[k]['n']} ({ftypes[k]['size_human_readable']})</li>"
        if "in .zip" in k:
            zip_html += line
        else:
            html += line

    html = "<ul>" + html
    if len(zip_html) > 0:
        html += f"<li>Zip contents:<ul>{zip_html}</ul>"
    html += "</ul>"
    
    return html

def summarise_study_filetypes(ftypes: dict) -> dict:
    """Summarise the filetype info for a study
    
    Summarise the filetype information for a study and if the study
    has enumerated files in zips have a section for these.
    """
    total_size_in_bytes = sum([
        v["size_in_bytes"] 
        for k, v in ftypes.items()
        if not k.endswith(" in .zip")
    ])
    n_files_excluding_zip_contents = sum([
        v["n"] 
        for k, v in ftypes.items()
        if not k.endswith(" in .zip")
    ])
    n_files_including_zip_contents = sum([
        v["n"] 
        for k, v in ftypes.items()
    ])
    return {
        "n_files_including_zip_contents": n_files_including_zip_contents,
        "n_files_excluding_zip_contents": n_files_excluding_zip_contents,
        "study_size_in_bytes": total_size_in_bytes, 
        "study_size_human_readable": sizeof_fmt(total_size_in_bytes), 
        "study_size": sizeof_fmt(total_size_in_bytes)
    }

@click.command()
@click.argument("accession_id")
def main(accession_id: str) -> None:
    """Summarise the sizes of filetypes in a study

    Summarise the sizes of filetypes in a study. For studies with zip
    files, the filetypes of the contents of the zip are also considered.
    """
    
    logging.basicConfig(level=logging.INFO)

    accession_id = sys.argv[1]

    bia_study = load_and_annotate_study(accession_id)
    ftypes = summarise_fileref_filetypes(bia_study.file_references)
    ftypes_html = filetypes_as_html(ftypes)
    ftypes_summary = {"filetype_breakdown": ftypes} | {"filetype_breakdown_html": ftypes_html} | summarise_study_filetypes(ftypes) 
    for k, v in ftypes_summary.items():
        annotation = StudyAnnotation(
            #ToDo: Should we configure env variable for snakemat_pipeline email?
            #author_email="snakemake_pipeline@ebi.ac.uk",
            author_email=settings.bia_username,
            accession_id=accession_id,
            key=k,
            value=str(v),
            state="active"
        )
        persist_study_annotation(bia_study.uuid, annotation)
    logger.info(ftypes_summary)

if __name__ == "__main__":
    main()

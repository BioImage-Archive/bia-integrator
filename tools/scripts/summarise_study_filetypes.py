import sys
from pathlib import Path
import logging

import click

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.cli import sizeof_fmt
from bia_integrator_core.models import StudyAnnotation
from bia_integrator_core.interface import persist_study_annotation

logger = logging.getLogger(__file__)

def _get_extension(p):
    ext = Path(p).suffix.lower()
    if ext == ".jpeg":
        return ".jpg"
    elif ext == ".tiff":
        return ".tif"
    else:
        return ext


def get_study_filetypes(accession_id: str) -> dict:
    """Return number of files of each type and sum of their sizes

    Return a dict with filetype extension as keys and a dict of
    info for each filetype:
        - number of files
        - total size in bytes
        - formatted total size
    """

    bia_study = load_and_annotate_study(accession_id)
    
    file_references = bia_study.file_references
    ftypes = {}

    for f in file_references.values():
        ext = _get_extension(f.name)
        uri_ext = _get_extension(f.uri)
        #if len(ext) == 0 and f.size_in_bytes == 0:
        if f.size_in_bytes == 0:
            continue
        if len(ext) == 0:
            ext = "none"
        if ext != uri_ext:
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

def study_filetypes_as_html(ftypes: dict) -> str:
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
        html += f"<li>Zip contents (not included it study totals above):<ul>{zip_html}</ul>"
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
    ftypes = get_study_filetypes(accession_id)
    ftypes_html = study_filetypes_as_html(ftypes)
    ftypes_summary = {"filetype_breakdown": ftypes} | {"filetype_breakdown_html": ftypes_html} | summarise_study_filetypes(ftypes) 
    for k, v in ftypes_summary.items():
        annotation = StudyAnnotation(
            accession_id=accession_id,
            key=k,
            value=str(v)
        )
        persist_study_annotation(annotation)
    logger.info(ftypes_summary)

if __name__ == "__main__":
    main()

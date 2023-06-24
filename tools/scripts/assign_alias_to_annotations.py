"""Assign aliases to all annotations in a study. Needs update for zips"""

import click
import logging

from bia_integrator_core.config import settings
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_study
from bia_integrator_tools.utils import get_annotation_files_by_accession

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')

def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    annfiles = get_annotation_files_by_accession(accession_id)
    aliases = [fileref for fileref in annfiles
                if fileref.attributes.get('alias')]
    if not aliases:
        i = 1
        for fileref in annfiles:
            al_id ="AN"+str(i)
            bia_study.file_references[fileref.id].attributes['alias'] = al_id
            i +=1
        persist_study(bia_study)
    else:
        last_id = len(aliases)+1
        for fileref in annfiles:
            if fileref not in aliases:
                al_id ="AN"+str(last_id)
                bia_study.file_references[fileref.id].attributes['alias'] = al_id
                last_id +=1
        persist_study(bia_study)

if __name__ == "__main__":
    main()
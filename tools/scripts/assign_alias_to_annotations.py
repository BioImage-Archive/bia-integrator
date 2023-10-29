"""Assign aliases to all annotations in a study. Needs update for zips"""

import click
import logging

from bia_integrator_api.models import BIAImageAlias
from bia_integrator_core.config import settings
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import get_filerefs, persist_filerefs
from bia_integrator_tools.utils import get_annotation_files_by_accession

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')

def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    file_references = get_filerefs(accession_id)
    dict_file_references = {fileref.uuid : fileref for fileref in file_references}
    annfiles = get_annotation_files_by_accession(accession_id)
    aliases = [fileref for fileref in annfiles
                if fileref.attributes.get('alias')]
    if not aliases:
        i = 1
        for fileref in annfiles:
            al_id = f"AN{i}"
            dict_file_references[fileref.uuid].attributes['alias'] = BIAImageAlias(name=al_id)
            i +=1
        persist_filerefs(file_references)
    else:
        last_id = len(aliases)+1
        for fileref in annfiles:
            if fileref not in aliases:
                al_id ="AN"+str(last_id)
                dict_file_references[fileref.uuid].attributes['alias'] = BIAImageAlias(name=al_id)
                last_id +=1
        persist_filerefs(file_references)

if __name__ == "__main__":
    main()
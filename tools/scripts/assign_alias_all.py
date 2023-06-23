import click
import logging

from openapi_client import models as api_models
from bia_integrator_core.config import settings
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import (
    persist_image_alias,
    get_aliases
)
import re

logger = logging.getLogger(__file__)


@click.command()
@click.argument('study_accession_id')

def main(study_accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(study_accession_id)
    
    current_alias = 1
    all_aliases = get_aliases(study_accession_id)
    if all_aliases:
        # assumes no gaps or if any ignores them and starts from the last alias
        all_image_ids = sorted([alias.name for alias in all_aliases])
        last_alias_name = all_image_ids[-1]
        current_alias = int(re.search(r'IM(.*)', last_alias_name))+1
    
    for image_id in bia_study.images:
        alias_name = "IM"+str(current_alias) 
        alias = api_models.BIAImageAlias(
                name=alias_name
            )
        persist_image_alias(image_id, alias)
        current_alias += 1

if __name__ == "__main__":
    main()
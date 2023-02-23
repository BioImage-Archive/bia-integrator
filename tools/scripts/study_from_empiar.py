import json
from typing import Optional

import click
import requests
from pydantic import BaseModel
from bia_integrator_core.models import BIAStudy, BIAImage, BIAImageRepresentation, Author
from bia_integrator_core.interface import persist_study

from ruamel.yaml import YAML


class EMPIARAuthor(BaseModel):
    
    name: str
    author_orcid: Optional[str]


def parse_empiar_authors(raw_obj):
    entry_dict = list(raw_obj.values())[0]
    author_dictlist = entry_dict['authors']
    authors = [EMPIARAuthor.parse_obj(entry['author']) for entry in author_dictlist]
    return authors
    

def get_empiar_file_uri(accession_no, relpath):
    
    return f"https://hl.fire.sdo.ebi.ac.uk/imaging-public/world_availability/{accession_no}/data/{relpath}"


@click.command()
@click.argument("definition_yaml_fpath")
def main(definition_yaml_fpath):
    yaml = YAML()

    with open(definition_yaml_fpath) as fh:
        config_dict = yaml.load(fh)

    accession_id = config_dict["accession_id"]
    accession_no = accession_id.split("-")[1]
    organism = config_dict["organism"]
    imaging_type = config_dict["imaging_type"]

    empiar_uri = f"https://www.ebi.ac.uk/empiar/api/entry/{accession_no}"
    example_image_uri = f"https://www.ebi.ac.uk/pdbe/emdb-empiar/entryIcons/{accession_no}-l.gif"

    r = requests.get(empiar_uri)
    raw_data = json.loads(r.content)
    empiar_authors = parse_empiar_authors(raw_data)

    images = {}
    for image_id, imdesc in config_dict["images"].items():
        relpath = imdesc["relpath"]
        uri = get_empiar_file_uri(accession_no, relpath)

        rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            uri=uri,
            size=0,
            type="fire_object"
        )

        images[image_id] = BIAImage(
            id=image_id,
            representations=[rep],
            original_relpath=relpath
        )

    bia_study = BIAStudy(
        accession_id=accession_id,
        release_date=raw_data[accession_id]['release_date'],
        title=raw_data[accession_id]['title'],
        description=raw_data[accession_id]['title'],
        organism=organism,
        imaging_type=imaging_type,
        example_image_uri=example_image_uri,
        images=images,
        authors = [Author.parse_obj(a.__dict__) for a in empiar_authors]
    )

    persist_study(bia_study)

    
if __name__ == "__main__":
    main()
import json

import click
import requests
from bia_integrator_core.models import BIAStudy, BIAImage, BIAImageRepresentation
from bia_integrator_core.interface import persist_study

from ruamel.yaml import YAML

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
        images=images
    )

    persist_study(bia_study)

    
if __name__ == "__main__":
    main()
import uuid
import hashlib
import logging

import parse
import typer
from ruamel.yaml import YAML

from bia_integrator_core.models import BIAImage, BIAImageRepresentation
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_image

from bia_integrator_tools.representations import StructuredFileset


app = typer.Typer()


logger = logging.getLogger(__file__)


def find_fileref_structure_mapping(bia_study, parse_template):
    """Generate the mapping betweeen image structure (e.g. Z plane and channel)
    and file reference. Example for channels:
    
    "structure": {
        "C_0000": "d93c4a37-a3b4-460d-a335-ab51d6808e5f",
        "C_0001": "4270be60-51e5-44f6-9607-bfe9172344fe",
        "C_0002": "a7f24a56-9c91-4125-b633-752329af6e99",
        "C_0003": "12980c81-1075-449c-880b-37e1beb6f4da"
    },
    "pattern": "C_<0000-0003>.tif"
    """

    structure = {}
    for fid, fileref in bia_study.file_references.items():
        result = parse.parse(parse_template, fileref.name)
        if result:
            k = "Z_{z:04d}".format(z=result.named['z'])
            structure[k] = fid

    pattern = "Z_<0001-0059>.tif"

    return structure, pattern


def find_fileref_structure_mapping_complex(bia_study, parse_template):
    """Generate the mapping betweeen image structure (e.g. Z plane and channel)
    and file reference. Example for channels:
    
    "structure": {
        "C_0000": "d93c4a37-a3b4-460d-a335-ab51d6808e5f",
        "C_0001": "4270be60-51e5-44f6-9607-bfe9172344fe",
        "C_0002": "a7f24a56-9c91-4125-b633-752329af6e99",
        "C_0003": "12980c81-1075-449c-880b-37e1beb6f4da"
    },
    "pattern": "C_<0000-0003>.tif"
    """

    component_map = {
        "Axon": "C_0000",
        "Oligodendrocyte": "C_0001",
        "Nucleus": "C_0002"
    }

    fileref_ids = []
    structure = {}
    for fid, fileref in bia_study.file_references.items():
        result = parse.parse(parse_template, fileref.name)
        if result:
            component = result.named["component"]
            if component in component_map:
                structure_key = component_map[component]
                structure[structure_key] = fid
                fileref_ids.append(fid)

    pattern = "C_<0000-0002>.tif"

    image_id = identifier_from_fileref_ids(fileref_ids)


    return structure, pattern, image_id


# FIXME - library code
def identifier_from_fileref_ids(fileref_ids):
    hash_input = ''.join(fileref_ids)
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
    image_id = str(image_id_as_uuid)    

    return image_id




@app.command()
def assign_images_from_yaml(yaml_fpath):
    logging.basicConfig(level=logging.INFO)

    yaml = YAML()
    with open(yaml_fpath) as fh:
        raw_config = yaml.load(fh)

    accession_id = raw_config['accession_id']
    bia_study = load_and_annotate_study(accession_id)

    # by_plane = {}
    fileref_map = {}
    for name, image_description in raw_config['images'].items():
        parse_template = image_description['parse_template']

        for fid, fileref in bia_study.file_references.items():
            result = parse.parse(parse_template, fileref.name)
            if result:
                z = result.named['z']
                # map_key = (0, 0, z)
                # fileref_map[map_key] = fid
                # by_plane[z] = fid
                fileref_map[fid] = (0, 0, z)


        # fileref_ids = list(by_plane.values())
        fileref_ids = list(fileref_map.keys())
        filerefs = [bia_study.file_references[fid] for fid in fileref_ids]

        image_id = identifier_from_fileref_ids(fileref_ids)

        sf = StructuredFileset(
            # by_plane=by_plane,
            fileref_map=fileref_map,
            attributes=image_description['attributes']
        )

        image_rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            size=sum(fileref.size_in_bytes for fileref in filerefs),
            uri=[fileref.uri for fileref in filerefs],
            attributes={
                "structured_fileset": sf.dict()
            },
            type="structured_fileset",
            dimensions=None,
            rendering=None
        )       

        image = BIAImage(
            id=image_id,
            accession_id=accession_id,
            original_relpath=name,
            name=name,
            representations=[image_rep]
        )

        persist_image(image)


if __name__ == "__main__":
    app()
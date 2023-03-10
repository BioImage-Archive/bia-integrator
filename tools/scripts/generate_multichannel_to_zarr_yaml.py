"""Generate yaml file for conversion of study artefacts to zarr format"""

import logging
import re

import click
from ruamel.yaml import YAML

from bia_integrator_core.integrator import load_and_annotate_study

logger = logging.getLogger(__file__)

@click.command()
@click.argument("accession_id")
@click.argument("image_name")
@click.argument("regex")
@click.argument("channel_col_ref")
@click.argument("output_path")
def main(accession_id, image_name, regex, channel_col_ref, output_path):
    logging.basicConfig(level=logging.INFO)
    
    matcher = re.compile(regex)

    bia_study = load_and_annotate_study(accession_id)
    # We assume the channel names correspond to the alphabetical order
    # of the original filenames. e.g.
    # file00 -> first channel name
    # file01 -> second channel name
    # etc.
    file_references = bia_study.file_references
    fileref_details = [
        (f.name, f.id) for f in file_references.values()
        if matcher.search(f.name) is not None
    ]
    assert len(fileref_details) > 0, "Regex did not produce any filerefs"
    filerefs = [fd[1] for fd in sorted(fileref_details)]
    
    channel_names = [
        #getattr(file_references[fileref], channel_col_ref)
        file_references[fileref].attributes[channel_col_ref]
        for fileref in filerefs
    ]

    # Write details required to generate representation to yaml
    rep_details = {
        "accession_id": accession_id,
        "images": {
            "description": {
                "name": image_name,
                "fileref_ids": filerefs,
                "attributes": {
                    "bioformats_conversion_type": "multiple_channels_to_zarr",
                    # No pattern, so generating script uses generic pattern
                    "channel_names": channel_names,
                }
            }
        }
    }
    yaml = YAML()
    yaml.default_flow_style = False
    with open(output_path, "w") as fid:
        yaml.dump(rep_details, fid)
    logger.info(f"Written output to {output_path}")

if __name__ == "__main__":
    main()

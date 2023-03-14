"""Generate yaml file for conversion of study artefacts to zarr format"""

import logging
import re

import click
from ruamel.yaml import YAML, CommentedSeq

from bia_integrator_core.integrator import load_and_annotate_study

logger = logging.getLogger(__file__)

@click.command()
@click.argument("accession_id")
@click.argument("image_name")
@click.argument("regex")
@click.argument("output_path")
@click.option("--channel-column", help="Column from filelist containing info about channel labels/names. This option cannot be used with '--channel-names'", default=None)
@click.option("--channel-names", help="Delimited names of channels. This option cannot be used with '--channel-column'. Default delimiter is ','. Use '--channel-names-delimiter' to change this.", default=None)
@click.option("--channel-names-delimiter", help="Delimited names of channels. This option cannot be used with '--channel-column'. Default delimiter is ','.", default=",")
def main(
    accession_id,
    image_name,
    regex, 
    output_path,
    channel_column,
    channel_names,
    channel_names_delimiter
    ):
    logging.basicConfig(level=logging.INFO)
    
    # Ensure both channel_column and channel_name are not supplied
    assert channel_column is None or channel_names is None, "Only one of --channel-column and --channel-names can be specified"

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
    fileref_details.sort()
    filerefs = [fd[1] for fd in fileref_details]
    logger.info(f"filerefs: {fileref_details}")
    
    if channel_column is not None:
        channel_names = [
            #getattr(file_references[fileref], channel_column)
            file_references[fileref].attributes[channel_column]
            for fileref in filerefs
        ]
    else:
        channel_names = [c.strip() for c in channel_names.split(channel_names_delimiter) if len(c.strip()) > 0]

    # Add as comments uris to filerefs
    fileref_ids = CommentedSeq(filerefs)
    for i, (filename, _) in enumerate(fileref_details):
        fileref_ids.yaml_add_eol_comment(filename, i)

    # Write details required to generate representation to yaml
    rep_details = {"accession_id":  accession_id,
        "images": {
            "description": {
                "name": image_name,
                "fileref_ids": fileref_ids,
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

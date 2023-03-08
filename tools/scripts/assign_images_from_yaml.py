import uuid
import hashlib
import logging

import shutil
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from pydantic import BaseSettings
from bia_integrator_tools.io import copy_local_zarr_to_s3
from bia_integrator_tools.conversion import run_zarr_conversion

import click
from ruamel.yaml import YAML

from bia_integrator_core.models import BIAImage, BIAImageRepresentation
from bia_integrator_core.interface import persist_image
from bia_integrator_core.integrator import load_and_annotate_study


logger = logging.getLogger(__file__)

def update_channel_names_zattrs(zattrs_path: Path, channel_names: list):
    """Update the names of channels in .zattrs

    """
    n_channels = len(channel_names)
    if not zattrs_path.is_file():
        logger.error(f"Could not find {zattrs_path}. Channel details not updated in .zattrs")
        return
        
    zattrs = json.loads(zattrs_path.read_text())
    try:
        n_zarr_channels = len(zattrs["omero"]["channels"])
    except KeyError:
        n_zarr_channels = 0
    except Exception as err:
        logger.error(f"An error occured. Channel details not updated in .zattrs. Error was {err}")
        return

    if n_zarr_channels != n_channels:
        logger.error(f"Expected {n_channels} channels, got {n_zarr_channels}: Channel details not updated in {zattrs_path}")
        return

    for channel, channel_name in enumerate(channel_names):
        zattrs["omero"]["channels"][channel]["label"] = channel_name

    zattrs_path.write_text(json.dumps(zattrs, indent=2))
    logger.info(f"Updated channel details in {zattrs_path}")

def update_channel_names_xml(xml_path: Path, channel_names: list):
    """Update the names of channels in OME xml file

    """
    n_channels = len(channel_names)
    if not xml_path.is_file():
        logger.error(f"Could not find {xml_path}. Channel details not updated.")
        return
        
    element_tree = ET.parse(xml_path)
    root = element_tree.getroot()
    xml_channels = [descendant for descendant in root.iter() if descendant.tag.endswith("Channel")]

    n_xml_channels = len(xml_channels)
    if n_xml_channels != n_channels:
        logger.error(f"Expected {n_channels} channels, got {n_xml_channels}: Channel details not updated in {xml_path}")
        return

    for xml_channel, channel_name in zip(xml_channels, channel_names):
        xml_channel.set("Name", channel_name)

    element_tree.write(xml_path)
    logger.info(f"Updated channel details in {xml_path}")

def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    with requests.get(src_uri, stream=True) as r:
        with open(dst_fpath, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)

def convert_multichannel_to_zarr_and_upload(
    accession_id,
    image_id,
    src_uris,
    pattern,
    channel_names=None
):
    """Convert image made from multiple single channel images to single zarr and upload to S3

    """
    bia_study = load_and_annotate_study(accession_id)
    dst_dir_basepath = Path("tmp/c2z")/accession_id
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)
    
    for src_uri in src_uris:
        dst_fpath = dst_dir_basepath/Path(src_uri).name
        if dst_fpath.exists():
            logger.info(f"{dst_fpath} exists. Skipping fetch")
        else:
            copy_uri_to_local(src_uri, dst_fpath)

    # Create pattern file in same dir as downloaded images
    dst_fpath = dst_dir_basepath/f"{image_id}.pattern"
    dst_fpath.write_text(pattern)

    # Do conversion using pattern file
    zarr_fpath = dst_dir_basepath/f"{image_id}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(dst_fpath, zarr_fpath)

        # Update channel info before copying to S3
        if channel_names is not None and len(channel_names) > 0:
            update_channel_names_xml(zarr_fpath/"OME"/"METADATA.ome.xml", channel_names)
            update_channel_names_zattrs(zarr_fpath/"0"/".zattrs", channel_names)

    # Copy to S3
    zarr_image_uri = copy_local_zarr_to_s3(zarr_fpath, accession_id, image_id)

@click.command()
@click.argument("yaml_fpath")
def main(yaml_fpath):
    logging.basicConfig(level=logging.INFO)

    yaml = YAML()
    with open(yaml_fpath) as fh:
        raw_config = yaml.load(fh)

    accession_id = raw_config['accession_id']
    bia_study = load_and_annotate_study(accession_id)

    for image_description in raw_config['images'].values():
        name = image_description['name']
        fileref_ids = image_description['fileref_ids']
        
        # Do we need to sort fileref_ids to prevent changes in position
        # in list from creating a new uuid?
        hash_input = ''.join(fileref_ids)
        hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
        image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
        image_id = str(image_id_as_uuid)

        filerefs = [bia_study.file_references[id] for id in fileref_ids]

        image_rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            size=sum(fileref.size_in_bytes for fileref in filerefs),
            uri=[fileref.uri for fileref in filerefs],
            attributes={"fileref_ids": fileref_ids},
            type="multi_fileref"
        )
        # Get other attributes
        for attr, value in image_description["attributes"].items():
            image_rep.attributes[attr] = value

        image = BIAImage(
            id=image_id,
            accession_id=accession_id,
            original_relpath=name,
            name=name,
            representations=[image_rep]
        )

        persist_image(image)

        bioformats_conversion_type = image_ref.attributes["bioformats_conversion_type"]
        if bioformats_conversion_type == "multiple_channels_to_zarr":
            convert_multichannel_to_zarr_and_upload(
                accession_id=image_rep.accession_id,
                image_id=image_rep.image_id,
                src_uris=image_rep.uri,
                channel_names=image_rep.attributes["channel_names"],
                pattern=image_rep.attributes["pattern"]
            )
        elif bioformats_conversion_type == "":
            
        else:
            logger.error("No converter for f{bioformats_conversion_type}")


if __name__ == "__main__":
    main()

import logging
import click
import json
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImage, ImageAnnotation
from bia_integrator_core.interface import persist_image_annotation

logger = logging.getLogger(__file__)

def sanitise_image_metadata(metadata: dict) -> dict:
    """Filter out entries with no information

    Filter out entries in metadata with no information. This sometimes
    needs to recursively look through dicts which are nested.
    """ 

    # Get keys and exclude those ending with '_unit' for special treatment
    # The are only included if associated with a value.
    metadata_keys = [k for k in metadata.keys() if not k.endswith("_unit")]

    sanitised = {}
    for metadata_key in metadata_keys:
        metadata_value = metadata[metadata_key]
        if metadata_value is None or metadata_value == "null":
            continue
        elif type(metadata_value) is list:
            if len(metadata_value) == 0:
                continue
            else:
                sanitised_metadata_value = []
                for metadata_value_item in metadata_value:
                    if metadata_value_item is None:
                        continue
                    elif type(metadata_value_item) is dict:
                        metadata_value_temp = sanitise_image_metadata(metadata_value_item)
                        if len(metadata_value_temp) > 0:
                            sanitised_metadata_value.append(metadata_value_temp)
                if len(sanitised_metadata_value) > 0:
                    sanitised[metadata_key] = sanitised_metadata_value
        elif type(metadata_value) is dict:
            sanitised_metadata_value = sanitise_image_metadata(metadata_value)
            if len(sanitised_metadata_value) > 0:
                sanitised[metadata_key] = sanitised_metadata_value
            else:
                continue
        else:
            sanitised[metadata_key] = metadata_value

        # Add units if they exist
        try:
            metadata_key_unit = metadata_key + "_unit"
            sanitised[metadata_key_unit] = metadata[metadata_key_unit]
        except KeyError:
            continue

    return sanitised

def get_image_metadata(image: BIAImage):
    largest_zarr_image = image.ome_metadata.images[0]
    first_image_metadata = json.loads(largest_zarr_image.pixels.json())

    return sanitise_image_metadata(first_image_metadata)

@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]

    print(get_image_metadata(image))
    for k, v in get_image_metadata(image).items():
        annotation = ImageAnnotation(
            accession_id=accession_id,
            image_id=image_id,
            key=k,
            value=str(v)
        )

        persist_image_annotation(annotation)


if __name__ == "__main__":
    main()

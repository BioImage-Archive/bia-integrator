"""Ad hoc script to select images to convert based on size"""

import typer
from bia_converter_light.config import api_client
from bia_converter_light.utils import in_bioformats_single_file_formats_list

PAGE_SIZE_DEFAULT = 10000000


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


app = typer.Typer()


def get_details_of_images_that_can_be_converted(accession_id: str):
    study = api_client.search_study_by_accession(accession_id)
    assert study
    datasets = api_client.get_dataset_linking_study(
        study.uuid, page_size=PAGE_SIZE_DEFAULT
    )
    file_references = []
    for dataset in datasets:
        file_references.extend(
            api_client.get_file_reference_linking_dataset(
                dataset.uuid, PAGE_SIZE_DEFAULT
            )
        )

    convertible_file_references = [
        {
            "accession_id": accession_id,
            "study_uuid": study.uuid,
            "name": fr.file_path,
            "uuid": fr.uuid,
            "size_in_bytes": fr.size_in_bytes,
            "size_human_readable": sizeof_fmt(fr.size_in_bytes),
        }
        for fr in file_references
        if in_bioformats_single_file_formats_list(fr.file_path)
    ]

    convertible_file_references = sorted(
        convertible_file_references, key=lambda fr: fr["size_in_bytes"], reverse=True
    )
    return convertible_file_references


@app.command()
def print_details_of_convertible_images(accession_id: str):
    """
    Print details of images that can be converted.
    """

    convertible_file_references = get_details_of_images_that_can_be_converted(
        accession_id
    )
    for cfr in convertible_file_references:
        print(
            f"{cfr['accession_id']}\t{cfr['study_uuid']}\t{cfr['name']}\t{cfr['uuid']}\t{cfr['size_in_bytes']}\t{cfr['size_human_readable']}"
        )


if __name__ == "__main__":
    app()

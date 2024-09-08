import typer
from pathlib import Path
from typing import List
from typing_extensions import Annotated
from bia_ingest_sm.biostudies import load_submission
from bia_ingest_sm.conversion.study import get_study
from bia_ingest_sm.conversion.experimental_imaging_dataset import (
    get_experimental_imaging_dataset,
)
from bia_ingest_sm.conversion.file_reference import get_file_reference_by_dataset
from bia_ingest_sm.conversion.specimen import get_specimen
from bia_ingest_sm.conversion.image_acquisition import get_image_acquisition
from bia_ingest_sm.conversion.image_annotation_dataset import (
    get_image_annotation_dataset,
)
from bia_ingest_sm.conversion.annotation_method import get_annotation_method
from bia_ingest_sm.conversion.image_representation import create_image_representation
from bia_ingest_sm.conversion.utils import get_bia_data_model_by_uuid, persist

# from bia_ingest_sm.image_utils import convert_image
from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
from bia_shared_datamodels import bia_data_model
from bia_ingest_sm.image_utils import image_utils
from bia_ingest_sm.image_utils.io import stage_fileref_and_get_fpath, copy_local_to_s3
from bia_ingest_sm.image_utils.conversion import cached_convert_to_zarr_and_get_fpath
from bia_ingest_sm.image_utils.rendering import generate_padded_thumbnail_from_ngff_uri

import logging
from rich import print
from rich.logging import RichHandler
from .cli_logging import tabulate_errors, IngestionResult

app = typer.Typer()


logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)

logger = logging.getLogger()

representations_app = typer.Typer()
app.add_typer(
    representations_app,
    name="representations",
    help="Create/list specified representations",
)


@app.command(help="Ingest from biostudies and echo json of bia_data_model.Study")
def ingest(
    accession_id_list: Annotated[List[str], typer.Argument()],
    verbose: Annotated[bool, typer.Option("-v")] = False,
) -> None:
    if verbose:
        logger.setLevel(logging.DEBUG)

    result_summary = {}

    for accession_id in accession_id_list:
        print(f"[blue]-------- Starting ingest of {accession_id} --------[/blue]")
        logger.debug(f"starting ingest of {accession_id}")

        result_summary[accession_id] = IngestionResult()

        submission = load_submission(accession_id)

        get_study(submission, result_summary, persist_artefacts=True)

        experimental_imaging_datasets = get_experimental_imaging_dataset(
            submission, result_summary, persist_artefacts=True
        )

        image_annotation_datasets = get_image_annotation_dataset(
            submission, result_summary, persist_artefacts=True
        )

        get_file_reference_by_dataset(
            submission,
            experimental_imaging_datasets + image_annotation_datasets,
            result_summary,
            persist_artefacts=True,
        )

        get_image_acquisition(submission, result_summary, persist_artefacts=True)

        # Specimen
        # Biosample and Specimen artefacts are processed as part of bia_data_models.Specimen (note - this is very different from Biostudies.Specimen)
        get_specimen(submission, result_summary, persist_artefacts=True)

        get_annotation_method(submission, result_summary, persist_artefacts=True)

        # typer.echo(study.model_dump_json(indent=2))

        logger.debug(f"COMPLETED: Ingest of: {accession_id}")
        print(f"[green]-------- Completed ingest of {accession_id} --------[/green]")

    print(tabulate_errors(result_summary))


@representations_app.command(help="Create specified representations")
def create(
    accession_id: Annotated[str, typer.Argument()],
    file_reference_uuid_list: Annotated[List[str], typer.Argument()],
) -> None:
    """Create representations for specified file reference(s)"""

    submission = load_submission(accession_id)
    representation_use_types = [
        use_type.value for use_type in ImageRepresentationUseType
    ]
    result_summary = {accession_id: IngestionResult()}
    for file_reference_uuid in file_reference_uuid_list:
        for representation_use_type in representation_use_types:
            create_image_representation(
                submission,
                [
                    file_reference_uuid,
                ],
                representation_use_type=representation_use_type,
                # representation_location=representation_location,
                result_summary=result_summary,
                persist_artefacts=True,
            )


@representations_app.command(
    help="Convert images and create representations",
)
def convert_images(
    accession_id: Annotated[str, typer.Argument()],
    file_reference_uuid_list: Annotated[List[str], typer.Argument()],
) -> None:
    """Convert images and create representations for specified file reference(s)"""

    submission = load_submission(accession_id)
    representation_use_types = [
        use_type.value
        for use_type in ImageRepresentationUseType
        # "UPLOADED_BY_SUBMITTER",
        # "INTERACTIVE_DISPLAY",
        # "THUMBNAIL",
    ]
    result_summary = {accession_id: IngestionResult()}
    for file_reference_uuid in file_reference_uuid_list:
        representations = {}
        for representation_use_type in representation_use_types:
            representations[representation_use_type] = create_image_representation(
                submission,
                [
                    file_reference_uuid,
                ],
                representation_use_type=representation_use_type,
                # representation_location=representation_location,
                result_summary=result_summary,
                persist_artefacts=True,
            )
        # Get image uploaded by submitter and update representation
        representation = representations["UPLOADED_BY_SUBMITTER"]
        # TODO file_uri of this representation = that of file reference(s)
        file_reference = get_bia_data_model_by_uuid(
            representation.original_file_reference_uuid[0],
            bia_data_model.FileReference,
            submission.accno,
        )
        local_path_to_uploaded_by_submitter_rep = stage_fileref_and_get_fpath(
            file_reference
        )

        # Convert to zarr, get zarr metadata
        # TODO: verify format for setting s3 uris then add upload to s3
        representation = representations["INTERACTIVE_DISPLAY"]
        local_path_to_zarr = cached_convert_to_zarr_and_get_fpath(
            representation, local_path_to_uploaded_by_submitter_rep
        )
        pixel_metadata = image_utils.get_ome_zarr_pixel_metadata(local_path_to_zarr)

        def _format_pixel_metadata(key):
            value = pixel_metadata.pop(key, None)
            if isinstance(value, tuple):
                value = value[0]
            if isinstance(value, str):
                value = int(value)
            return value

        representation.size_x = _format_pixel_metadata("SizeX")
        representation.size_y = _format_pixel_metadata("SizeY")
        representation.size_z = _format_pixel_metadata("SizeZ")
        representation.size_c = _format_pixel_metadata("SizeC")
        representation.size_t = _format_pixel_metadata("SizeT")

        representation.attribute |= pixel_metadata

        representation.image_format = ".ome.zarr"
        file_uri = copy_local_to_s3(
            local_path_to_zarr,
            f"{submission.accno}/{representation.uuid}{representation.image_format}",
        )
        representation.file_uri = [
            file_uri,
        ]

        # Create thumbnail representation
        representation = representations["THUMBNAIL"]
        thumbnail = generate_padded_thumbnail_from_ngff_uri(
            local_path_to_zarr / "0", dims=(256, 256)
        )
        local_path_to_thumbnail = (
            Path("/home/kola/temp/") / f"{representation.uuid}.png"
        )
        with local_path_to_thumbnail.open("wb") as fh:
            thumbnail.save(fh)
        print(f"local_path_to_thumbnail = {local_path_to_thumbnail}")
        representation.image_format = ".png"
        file_uri = copy_local_to_s3(
            local_path_to_thumbnail,
            f"{submission.accno}/{representation.uuid}{representation.image_format}",
        )
        representation.file_uri = [
            file_uri,
        ]

        # Create static display (representative image) representation
        representation = representations["STATIC_DISPLAY"]
        static_display = generate_padded_thumbnail_from_ngff_uri(
            local_path_to_zarr / "0", dims=(512, 512)
        )
        local_path_to_static_display = (
            Path("/home/kola/temp/") / f"{representation.uuid}.png"
        )
        with local_path_to_static_display.open("wb") as fh:
            static_display.save(fh)
        print(f"local_path_to_static_display = {local_path_to_static_display}")
        representation.image_format = ".png"
        file_uri = copy_local_to_s3(
            local_path_to_static_display,
            f"{submission.accno}/{representation.uuid}{representation.image_format}",
        )
        representation.file_uri = [
            file_uri,
        ]

        persist(
            list(representations.values()),
            "image_representations",
            submission.accno,
        )


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()

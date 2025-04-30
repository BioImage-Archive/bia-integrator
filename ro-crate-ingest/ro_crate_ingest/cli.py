import typer
import logging
from typing import Annotated, Optional
from pydantic import RootModel
from ro_crate_ingest.crate_reader import process_ro_crate
from ro_crate_ingest.entity_conversion import (
    AnnotationMethod,
    BioSample,
    Dataset,
    ImageAcquisitionProtocol,
    Protocol,
    SpecimenImagingPreparationProtocol,
    Study,
    FileReference,
)
from pathlib import Path
from rich.logging import RichHandler

bia_ro_crate = typer.Typer()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


@bia_ro_crate.command("ingest")
def convert(
    crate_path: Annotated[
        Optional[Path],
        typer.Option(
            "--crate-path",
            "-c",
            case_sensitive=False,
            help="Path to the ro-crate root (or ro-crate-metadata.json)",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            case_sensitive=False,
        ),
    ] = Path(__file__).parents[1],
):

    entities = process_ro_crate(crate_path)

    api_objects = []

    study = Study.create_api_study(entities)
    api_objects.append(study)

    study_uuid = study.uuid

    datasets = Dataset.create_api_dataset(entities, study_uuid)
    api_objects += datasets
    api_objects += AnnotationMethod.create_api_image_acquisition_protocol(
        entities, study_uuid
    )
    api_objects += Protocol.create_api_protocol(entities, study_uuid)
    api_objects += BioSample.create_api_bio_sample(entities, study_uuid)
    api_objects += ImageAcquisitionProtocol.create_api_image_acquisition_protocol(
        entities, study_uuid
    )
    api_objects += SpecimenImagingPreparationProtocol.create_api_specimen_imaging_preparation_protocol(
        entities, study_uuid
    )

    api_objects += FileReference.create_file_reference(entities, study_uuid, crate_path)

    ApiModels = RootModel[list]
    write_out = ApiModels(api_objects)

    with open(output_dir / "combined_metadata.json", "w") as f:
        f.write(write_out.model_dump_json(indent=2))

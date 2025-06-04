from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import logging
import pathlib
import rdflib
from ro_crate_ingest.crate_reader import load_ro_crate_metadata_to_graph
from ro_crate_ingest.entity_conversion.FileReference import (
    find_files,
    create_api_file_reference,
)
from ro_crate_ingest.entity_conversion.CreationProcess import convert_creation_process

logger = logging.getLogger("__main__." + __name__)


def create_image_and_dependencies(
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
    crate_path: pathlib.Path,
) -> tuple[
    list[APIModels.FileReference],
    list[APIModels.CreationProcess],
    list[APIModels.Image],
]:
    ro_crate_images = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Image)
    )

    crate_graph = load_ro_crate_metadata_to_graph(crate_path)

    file_reference_list = []
    image_list = []
    creation_process_list = []

    for image in ro_crate_images:

        image_dataset = crate_objects_by_id[
            get_image_dataset_id(image.id, crate_graph, crate_path)
        ]

        file_references = convert_file_reference(
            image, study_uuid, image_dataset, crate_path
        )
        file_reference_list += file_references

        ro_crate_creaiton_process = crate_objects_by_id[image.resultOf.id]
        creation_process = convert_creation_process(
            ro_crate_creaiton_process, study_uuid
        )

        creation_process_list.append(creation_process)

        image_list.append(
            convert_image(
                image, study_uuid, file_references, creation_process.uuid, image_dataset
            )
        )

    return (file_reference_list, creation_process_list, image_list)


def get_image_dataset_id(image_id: str, graph: rdflib.Graph, crate_path: str) -> str:
    pathlib_path = pathlib.Path(crate_path) / image_id
    image_rdf_ref = pathlib_path.absolute().as_uri()
    subjects = list(
        graph.subjects(
            rdflib.URIRef("http://schema.org/hasPart"), rdflib.URIRef(image_rdf_ref)
        )
    )
    if len(subjects) == 0:
        logger.exception(f"No dataset found for image {image_id}.")
        raise ValueError(
            f"No dataset found for image {image_id}. Please check the RO-Crate metadata."
        )
    elif len(subjects) > 1:
        logger.exception(f"Multiple datasets found for image {image_id}.")
        raise ValueError(
            f"Multiple datasets found for image {image_id}. Please check the RO-Crate metadata."
        )
    else:
        dataset_id = pathlib.Path.from_uri(subjects[0]).relative_to(crate_path)
        return f"{str(dataset_id)}/"


def convert_file_reference(
    image: ROCrateModels.Image,
    study_uuid: str,
    dataset: ROCrateModels.Dataset,
    crate_path: pathlib.Path,
) -> list[APIModels.FileReference]:

    files = []

    # TODO: Handle types better, in case of different context useage - probably requires minor refactor of crate_reader to extract context once.
    if "Dataset" in image.type:
        file_paths = find_files(dataset, crate_path)
        for file_path in file_paths:
            files.append(
                create_api_file_reference(
                    str(file_path), study_uuid, dataset.id, crate_path
                )
            )
    elif "File" in image.type:
        files.append(
            create_api_file_reference(
                str(pathlib.Path(crate_path) / image.id),
                study_uuid,
                dataset.id,
                crate_path,
            )
        )

    else:
        # check path of object to determine if it is a file or dataset
        raise ValueError(
            f"Image {image.id} is missing Dataset or File type. Types found: {image.type}"
        )

    return files


def convert_image(
    image: ROCrateModels.Image,
    study_uuid: str,
    file_references: list[APIModels.FileReference],
    creation_process_uuid: str,
    image_dataset: ROCrateModels.Dataset,
):

    original_file_reference_uuids = [file_ref.uuid for file_ref in file_references]
    uuid_unique_string = " ".join(original_file_reference_uuids)

    image = {
        "uuid": str(uuid_creation.create_image_uuid(study_uuid, uuid_unique_string)),
        "submission_dataset_uuid": str(
            uuid_creation.create_dataset_uuid(study_uuid, image_dataset.id)
        ),
        "creation_process_uuid": creation_process_uuid,
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "original_file_reference_uuid": original_file_reference_uuids,
        "additional_metadata": [
            AttributeModels.DocumentUUIDUinqueInputAttribute(
                provenance=APIModels.Provenance.BIA_INGEST,
                name="uuid_unique_input",
                value={"uuid_unique_input": uuid_unique_string},
            ).model_dump()
        ],
    }

    return APIModels.Image(**image)

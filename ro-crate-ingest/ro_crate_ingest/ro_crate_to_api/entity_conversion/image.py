from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import logging
import pathlib
import rdflib
from ro_crate_ingest.ro_crate_to_api.entity_conversion.file_reference import (
    find_files,
    create_api_file_reference,
)
from ro_crate_ingest.ro_crate_to_api.entity_conversion.creation_process import (
    convert_creation_process,
)
from ro_crate_ingest.ro_crate_to_api.entity_conversion.image_dependency_ordering import (
    order_creation_processes_and_images,
)
from ro_crate_ingest.graph_utils import get_hasPart_parent_id_from_child


logger = logging.getLogger("__main__." + __name__)


def create_image_and_dependencies(
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
    crate_path: pathlib.Path,
    crate_graph: rdflib.Graph,
) -> tuple[
    list[APIModels.FileReference],
    list[str],
    dict[int, list[ROCrateModels.CreationProcess | ROCrateModels.Image]],
    int,
]:

    ro_crate_images = {
        id: obj
        for id, obj in crate_objects_by_id.items()
        if isinstance(obj, ROCrateModels.Image)
    }

    ro_crate_creation_processes = {
        id: obj
        for id, obj in crate_objects_by_id.items()
        if isinstance(obj, ROCrateModels.CreationProcess)
    }

    if len(ro_crate_images) == 0:
        return [], [], {}, 0

    ordered_image_creation_process_list, max_dependency_chain_length = (
        order_creation_processes_and_images(
            ro_crate_creation_processes, ro_crate_images
        )
    )

    file_reference_list = []
    file_path_list = []
    ordered_objects_to_create: dict[
        int, list[APIModels.CreationProcess | APIModels.Image]
    ] = {i: list() for i in range(max_dependency_chain_length + 1)}

    chain_length = 0
    while chain_length <= max_dependency_chain_length:
        if chain_length % 2 == 0:
            # Even chain length means it's a creation process
            for ro_crate_creation_process in ordered_image_creation_process_list[
                chain_length
            ]:
                ordered_objects_to_create[chain_length].append(
                    convert_creation_process(ro_crate_creation_process, study_uuid)
                )
        else:
            # Odd chain length means it's an image
            for image in ordered_image_creation_process_list[chain_length]:
                image_dataset = crate_objects_by_id[
                    get_hasPart_parent_id_from_child(image.id, crate_graph, crate_path)
                ]

                file_references, file_paths = convert_file_reference(
                    image, study_uuid, image_dataset, crate_path
                )
                file_reference_list += file_references
                file_path_list += file_paths

                ordered_objects_to_create[chain_length].append(
                    convert_image(
                        image,
                        study_uuid,
                        file_references,
                        image_dataset,
                    )
                )
        chain_length += 1

    return (
        file_reference_list,
        file_path_list,
        ordered_objects_to_create,
        max_dependency_chain_length,
    )


def convert_file_reference(
    image: ROCrateModels.Image,
    study_uuid: str,
    dataset: ROCrateModels.Dataset,
    crate_path: pathlib.Path,
) -> list[APIModels.Image]:

    dataset_uuid = str(uuid_creation.create_dataset_uuid(study_uuid, dataset.id))

    files = []
    file_paths = []

    # TODO: Handle types better, in case of different context useage - probably requires minor refactor of crate_reader to extract context once.
    if "Dataset" in image.type:
        file_paths = find_files(dataset, crate_path)
        for file_path in file_paths:
            file_paths.append(str(file_path))
            files.append(
                create_api_file_reference(
                    str(file_path), study_uuid, dataset_uuid, crate_path
                )
            )
    elif "File" in image.type:
        file_paths.append(pathlib.Path(crate_path) / image.id)
        files.append(
            create_api_file_reference(
                str(pathlib.Path(crate_path) / image.id),
                study_uuid,
                dataset_uuid,
                crate_path,
            )
        )

    else:
        # check path of object to determine if it is a file or dataset
        raise ValueError(
            f"Image {image.id} is missing Dataset or File type. Types found: {image.type}"
        )

    return files, file_paths


def convert_image(
    image: ROCrateModels.Image,
    study_uuid: str,
    file_references: list[APIModels.FileReference],
    image_dataset: ROCrateModels.Dataset,
):

    original_file_reference_uuids = [file_ref.uuid for file_ref in file_references]
    # uuid_unique_string = " ".join(original_file_reference_uuids)

    image = {
        "uuid": str(uuid_creation.create_image_uuid(study_uuid, image.id)),
        "submission_dataset_uuid": str(
            uuid_creation.create_dataset_uuid(study_uuid, image_dataset.id)
        ),
        "creation_process_uuid": str(
            uuid_creation.create_creation_process_uuid(study_uuid, image.resultOf.id)
        ),
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "original_file_reference_uuid": original_file_reference_uuids,
        "additional_metadata": [
            AttributeModels.DocumentUUIDUinqueInputAttribute(
                provenance=APIModels.Provenance.BIA_INGEST,
                name="uuid_unique_input",
                value={"uuid_unique_input": image.id},
            ).model_dump()
        ],
    }

    return APIModels.Image(**image)

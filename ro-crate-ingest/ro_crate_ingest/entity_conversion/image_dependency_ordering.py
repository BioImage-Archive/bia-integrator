import bia_shared_datamodels.ro_crate_models as ROCrateModels
from ro_crate_ingest.save_utils import persist, PersistenceMode


def calculate_dependency_chain_length(
    creation_process_by_id: dict[str, ROCrateModels.CreationProcess],
    image_by_id: dict[str, ROCrateModels.Image],
) -> dict[str, int]:
    """
    Images need their creation process to be added to the api before they can be added
    Some creation processes need images to be added to the api before they can be added
    dependecy_chain_length is the maximum number of times a change in type of object being added to the api has to occur before this object can be added to the api.
    E.g. with the chain:  IMG2 -> CP2, CP2 -> [IMG1], IMG1 -> CP1
    dependecy_chain_length = { CP1.uuid: 0, IMG1.uuid: 1, CP2.uuid: 2, IMG2.uuid: 3} (note images are always odd, creation processes are even inc. 0 )
    """
    dependecy_chain_length = {}

    for uuid, creation_process in creation_process_by_id.items():
        if uuid not in dependecy_chain_length.keys():
            creation_process_dependency_chain_length(
                creation_process,
                dependecy_chain_length,
                image_by_id,
                creation_process_by_id,
            )

    for uuid, image in image_by_id.items():
        if uuid not in dependecy_chain_length.keys():
            image_dependency_chain_length(
                image,
                dependecy_chain_length,
                image_by_id,
                creation_process_by_id,
            )
    return dependecy_chain_length


def creation_process_dependency_chain_length(
    creation_process: ROCrateModels.CreationProcess,
    dependency_chain_length: dict,
    images: dict[str, ROCrateModels.Image],
    creation_processes: dict[str, ROCrateModels.CreationProcess],
) -> int:
    id = creation_process.id

    # Creation processes either do not depend on any images (in which case dependency chain length is 0)
    # Or they need to be created after the last image they depend on gets created (so max(image dependency chain length) + 1)
    if id not in dependency_chain_length.keys():
        if not creation_process.inputImage or len(creation_process.inputImage) == 0:
            dependency_chain_length[id] = 0
        else:
            max_length = 0
            for image_uuid in creation_process.inputImage:
                img_chain_length = image_dependency_chain_length(
                    images[image_uuid],
                    dependency_chain_length,
                    images,
                    creation_processes,
                )
                if img_chain_length > max_length:
                    max_length = img_chain_length
            dependency_chain_length[id] = max_length + 1

    return dependency_chain_length[id]


def image_dependency_chain_length(
    image: ROCrateModels.Image,
    dependency_chain_length: dict,
    images: dict[str, ROCrateModels.Image],
    creation_processes: dict[str, ROCrateModels.CreationProcess],
) -> int:
    id = image.id

    # Images depend on at least 1 creation process, so always have a dependency chain length of: creation process dependcy chain length + 1
    if id not in dependency_chain_length.keys():
        if image.resultOf in dependency_chain_length.keys():
            dependency_chain_length[id] = dependency_chain_length[image.resultOf] + 1
        else:
            cp_id = image.resultOf
            cp_chain_length = creation_process_dependency_chain_length(
                creation_processes[cp_id],
                dependency_chain_length,
                images,
                creation_processes,
            )
            dependency_chain_length[id] = cp_chain_length + 1

    return dependency_chain_length[id]



def order_creation_processes_and_images(
    creation_process_by_id: dict[str, ROCrateModels.CreationProcess],
    image_by_id: dict[str, ROCrateModels.Image],
) -> tuple[dict[int, list[ROCrateModels.CreationProcess | ROCrateModels.Image]], int]:

    dependecy_chain_length = calculate_dependency_chain_length(
        creation_process_by_id, image_by_id
    )

    object_order: dict[int, list[ROCrateModels.CreationProcess | ROCrateModels.Image]] = {}
    max_chain_length = 0
    for uuid, chain_length in dependecy_chain_length.items():
        if chain_length not in object_order.keys():
            object_order[chain_length] = []

        if chain_length % 2 == 0:
            # Even chain length means it's a creation process
            object_order[chain_length].append(creation_process_by_id[uuid])
        else:
            # Odd chain length means it's an image
            object_order[chain_length].append(image_by_id[uuid])

        if chain_length > max_chain_length:
            max_chain_length = chain_length

    return object_order, max_chain_length

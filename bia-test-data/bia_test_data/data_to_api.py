from pathlib import Path
from dotenv import dotenv_values
from bia_integrator_api.api import PrivateApi
from bia_integrator_api import Configuration, ApiClient, exceptions
from pydantic.alias_generators import to_snake
import bia_integrator_api.models as api_models


def test_user_creation_details() -> dict[str, str]:
    env_path = Path(__file__).parents[2] / "api" / ".env_compose"
    container_env = dotenv_values(env_path)
    user_creation_token = container_env.get("USER_CREATE_SECRET_TOKEN")
    user_creation_details = {
        "email": "test@example.com",
        "password_plain": "test",
        "secret_token": user_creation_token,
    }
    return user_creation_details


def get_object_creation_client(
    api_base_url: str,
) -> PrivateApi:
    api_config = Configuration(host=api_base_url)
    private_api = PrivateApi(ApiClient(configuration=api_config))
    user_dict = test_user_creation_details()
    try:
        access_token = private_api.login_for_access_token(
            username=user_dict["email"], password=user_dict["password_plain"]
        )
    except exceptions.UnauthorizedException:
        private_api.register_user(api_models.BodyRegisterUser(**user_dict))
        access_token = private_api.login_for_access_token(
            username=user_dict["email"], password=user_dict["password_plain"]
        )

    assert access_token

    api_config.access_token = access_token.access_token

    return private_api


def calculate_dependency_chain_length(
    object_by_type: dict[str, dict[str, dict]]
) -> dict[str, int]:
    # Images need their creation process to be added to the api before they can be added
    # Some creation processes need images to be added to the api before they can be added
    # dependecy_chain_length is the maximum number of times a change in type of object being added to the api has to occur before this object can be added to the api.
    # E.g. with the chain:  IMG2 -> CP2, CP2 -> [IMG1], IMG1 -> CP1
    # dependecy_chain_length = { CP1.uuid: 0, IMG1.uuid: 1, CP2.uuid: 2, IMG2.uuid: 3} (note images are always odd, creation processes are even inc. 0 )
    dependecy_chain_length = {}

    for uuid, creation_process in object_by_type["CreationProcess"].items():
        if uuid not in dependecy_chain_length.keys():
            creation_process_dependency_chain_length(
                creation_process,
                dependecy_chain_length,
                object_by_type["Image"],
                object_by_type["CreationProcess"],
            )

    for uuid, image in object_by_type["Image"].items():
        if uuid not in dependecy_chain_length.keys():
            image_dependency_chain_length(
                image,
                dependecy_chain_length,
                object_by_type["Image"],
                object_by_type["CreationProcess"],
            )
    return dependecy_chain_length


def creation_process_dependency_chain_length(
    creation_process: dict,
    dependency_chain_length: dict,
    images: dict[str, dict],
    creation_processes: dict[str, dict],
) -> int:
    uuid = creation_process["uuid"]

    # Creation processes either do not depend on any images (in which case dependency chain length is 0)
    # Or they need to be created after the last image they depend on gets created (so max(image dependency chain length) + 1)
    if uuid not in dependency_chain_length.keys():
        if (
            not creation_process["input_image_uuid"]
            or len(creation_process["input_image_uuid"]) == 0
        ):
            dependency_chain_length[uuid] = 0
        else:
            max_length = 0
            for image_uuid in creation_process["input_image_uuid"]:
                img_chain_length = image_dependency_chain_length(
                    images[image_uuid],
                    dependency_chain_length,
                    images,
                    creation_processes,
                )
                if img_chain_length > max_length:
                    max_length = img_chain_length
            dependency_chain_length[uuid] = max_length + 1

    return dependency_chain_length[uuid]


def image_dependency_chain_length(
    image: dict,
    dependency_chain_length: dict,
    images: dict[str, dict],
    creation_processes: dict[str, dict],
) -> int:
    uuid = image["uuid"]

    # Images depend on at least 1 creation process, so always have a dependency chain length of: creation process dependcy chain length + 1
    if uuid not in dependency_chain_length.keys():
        if image["creation_process_uuid"] in dependency_chain_length.keys():
            dependency_chain_length[uuid] = (
                dependency_chain_length[image["creation_process_uuid"]] + 1
            )
        else:
            cp_uuid = image["creation_process_uuid"]
            cp_chain_length = creation_process_dependency_chain_length(
                creation_processes[cp_uuid],
                dependency_chain_length,
                images,
                creation_processes,
            )
            dependency_chain_length[uuid] = cp_chain_length + 1

    return dependency_chain_length[uuid]


def add_simple_dependecy_object(
    object_type: str, object_by_type: dict[str, dict], ordered_object_list: list
) -> None:
    if object_type in object_by_type.keys():
        for study in object_by_type[object_type].values():
            ordered_object_list.append(study)


def add_creation_processes_and_images(
    object_by_type: dict[str, dict], ordered_object_list: list[dict]
):
    if "CreationProcess" in object_by_type.keys() and "Image" in object_by_type.keys():

        dependecy_chain_length = calculate_dependency_chain_length(object_by_type)

        uuid_order: dict[int, list[str]] = {}
        max_chain_length = 0
        for uuid, chain_length in dependecy_chain_length.items():
            if chain_length not in uuid_order.keys():
                uuid_order[chain_length] = []
            uuid_order[chain_length].append(uuid)
            if chain_length > max_chain_length:
                max_chain_length = chain_length

        chain_length = 0
        while chain_length <= max_chain_length:
            for uuid in uuid_order[chain_length]:
                if uuid in object_by_type["CreationProcess"].keys():
                    ordered_object_list.append(object_by_type["CreationProcess"][uuid])
                else:
                    ordered_object_list.append(object_by_type["Image"][uuid])
            chain_length += 1

    elif "CreationProcess" in object_by_type.keys():
        add_simple_dependecy_object(
            "CreationProcess", object_by_type, ordered_object_list
        )
    elif "Image" in object_by_type.keys():
        add_simple_dependecy_object("Image", object_by_type, ordered_object_list)


def order_object_for_api(object_list: list[dict]):

    # Dictionary of form: { "object type": { "objecy_uuid": { ...object data... } } }
    object_by_type: dict[str, dict] = {}
    for object in object_list:
        object_type = object["model"]["type_name"]
        if object_type not in object_by_type:
            object_by_type[object_type] = {}
        object_by_type[object_type][object["uuid"]] = object

    ordered_object_list = []

    add_simple_dependecy_object("Study", object_by_type, ordered_object_list)
    add_simple_dependecy_object("Dataset", object_by_type, ordered_object_list)
    add_simple_dependecy_object("FileReference", object_by_type, ordered_object_list)
    add_simple_dependecy_object("Protocol", object_by_type, ordered_object_list)
    add_simple_dependecy_object("BioSample", object_by_type, ordered_object_list)
    add_simple_dependecy_object(
        "SpecimenImagingPreparationProtocol", object_by_type, ordered_object_list
    )
    add_simple_dependecy_object("Specimen", object_by_type, ordered_object_list)
    add_simple_dependecy_object(
        "ImageAcquisitionProtocol", object_by_type, ordered_object_list
    )
    add_simple_dependecy_object("AnnotationMethod", object_by_type, ordered_object_list)
    # Only images and creation process can depend on one another
    add_creation_processes_and_images(object_by_type, ordered_object_list)
    add_simple_dependecy_object(
        "ImageRepresentation", object_by_type, ordered_object_list
    )

    return ordered_object_list


def add_objects_to_api(api_base_url, object_list: list[dict]):
    private_client = get_object_creation_client(api_base_url)

    ordered_object_list = order_object_for_api(object_list)

    for bia_object_dict in ordered_object_list:
        bia_object_type = bia_object_dict["model"]["type_name"]
        post_method_name = "post_" + to_snake(bia_object_type)
        post_function = private_client.__getattribute__(post_method_name)
        get_method_name = "get_" + to_snake(bia_object_type)
        get_function = private_client.__getattribute__(get_method_name)
        api_obj = getattr(api_models, bia_object_type).model_validate(bia_object_dict)

        try:
            object_from_api = get_function(bia_object_dict["uuid"])
        except exceptions.NotFoundException:
            object_from_api = None

        if object_from_api:
            assert object_from_api == api_obj
        else:
            post_function(api_obj)

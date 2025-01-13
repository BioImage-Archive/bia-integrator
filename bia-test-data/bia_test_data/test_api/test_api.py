from python_on_whales import DockerClient
from pathlib import Path
from dotenv import dotenv_values
from bia_integrator_api.api import PrivateApi
from bia_integrator_api import Configuration, ApiClient
from pydantic.alias_generators import to_snake
import bia_integrator_api.models as api_models
import time

# TODO: update semantic version number in docker-compose.yaml
# suggest using: from configparser import ConfigParser


class TestAPI:
    docker_compose_yaml_path: str
    docker: DockerClient

    def __init__(self):
        self.docker_compose_yaml_path = Path(__file__).parent / "docker-compose.yaml"
        self.docker = DockerClient(compose_files=[str(self.docker_compose_yaml_path)])

    def start(self):
        self.docker.compose.pull()
        self.docker.compose.up(detach=True)
        all_running = False
        while not all_running:
            services = self.docker.compose.ps(all=True)
            all_running = all(
                service.state.health.status == "healthy" for service in services
            )
            if all_running:
                print("All services are healthy.")
                return
            print("Not all services are healthy (yet...)")
            time.sleep(2)

    def stop(self):
        self.docker.compose.down()


def test_user_creation_details() -> dict:
    env_path = Path(__file__).parents[3] / "api" / ".env_compose"
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
    private_api.register_user(user_dict)
    access_token = private_api.login_for_access_token(
        username=user_dict["email"], password=user_dict["password_plain"]
    )
    assert access_token

    api_config.access_token = access_token.access_token

    return private_api


def create_objects(api_base_url, object_list=list[dict]):
    private_client = get_object_creation_client(api_base_url)

    for bia_object in object_list:
        bia_object_type = bia_object["model"]["type_name"]
        client_method_name = "post_" + to_snake(bia_object_type)
        client_function = private_client.__getattribute__(client_method_name)

        api_obj = getattr(api_models, bia_object_type).model_validate(bia_object)

        client_function(api_obj)

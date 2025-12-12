import logging
from collections.abc import Callable
from enum import Enum
from uuid import UUID

from bia_integrator_api import ApiClient, Configuration
from bia_integrator_api.api import PrivateApi
from bia_integrator_api.exceptions import ApiException
from bia_shared_datamodels import bia_data_model
from pydantic import BaseModel
from pydantic.alias_generators import to_snake

from persistance.settings import Settings

logger = logging.getLogger("__main__." + __name__)


class EndpointType(str, Enum):
    POST = "post"
    GET = "get"


class BIAAPIClient(PrivateApi):
    """
    Wrapper around bia PrivateAPI to handle working out the correct endpoint to use for basic get/post operations.
    """

    def __init__(self, settings: Settings) -> None:
        api_config = Configuration(host=settings.bia_api_basepath)
        super().__init__(ApiClient(configuration=api_config))
        access_token = self.login_for_access_token(
            username=settings.bia_api_username, password=settings.bia_api_password
        )
        api_config.access_token = access_token.access_token

    def put_object(self, bia_api_object: BaseModel) -> None:
        """
        Attempts to put an object to the appropriate endpoint for the object.
        Will automatically bump the version if an object with the same uuid already exists.
        """
        post_function = self._get_basic_endpoint(
            type(bia_api_object), EndpointType.POST
        )
        try:
            post_function(bia_api_object)
        except ApiException as e:
            if e.reason == "Conflict":
                self.update_existing_object(bia_api_object)
            else:
                raise e

    def update_existing_object(self, bia_api_object: BaseModel) -> None:
        api_copy_of_obj = self.get_object_by_type(
            bia_api_object.uuid, type(bia_api_object)
        )
        post_function = self._get_basic_endpoint(
            type(bia_api_object), EndpointType.POST
        )
        if (
            api_copy_of_obj
            and self._round_trip_object_class_from_client_to_datamodel(bia_api_object)
            != api_copy_of_obj
        ):
            bia_api_object.version = api_copy_of_obj.version + 1
            post_function(bia_api_object)
        else:
            logging.warning(
                f"No changes in object: {bia_api_object.uuid}, therefore, not updating."
            )

    def get_object_by_type(
        self, uuid: UUID | str, object_type: str | type[BaseModel]
    ) -> BaseModel:
        get_endpoint = self._get_basic_endpoint(object_type, EndpointType.GET)
        return get_endpoint(str(uuid))

    @staticmethod
    def _object_type_to_endpoint_name(object_type: str | type[BaseModel]) -> str:
        if isinstance(object_type, type):
            return to_snake(object_type.__name__)
        else:
            return to_snake(object_type)

    def _get_basic_endpoint(
        self, object_type: str | type[BaseModel], endpoint_type: EndpointType
    ) -> Callable:
        """
        Returns the endpoint for all the post_X and get_X endpoints. Does not handle the get_X_linking_Y endpoints.
        """
        endpoint_type_name = self._object_type_to_endpoint_name(object_type)
        return getattr(self, f"{endpoint_type.value}_{endpoint_type_name}")

    @staticmethod
    def _round_trip_object_class_from_client_to_datamodel(api_object: BaseModel):
        """
        Converts objects from a bia-client model to the internal api data model.
        This automatically adds information from pydantic validators that the api will add,
        making the output more comparable to an object returned from the api.
        """
        obj_class_api = api_object.__class__
        bia_data_model_class = getattr(bia_data_model, obj_class_api.__name__)

        obj_bia_data_model = bia_data_model_class.model_validate_json(
            api_object.model_dump_json()
        )

        original_object = obj_class_api.model_validate_json(
            obj_bia_data_model.model_dump_json()
        )

        return original_object

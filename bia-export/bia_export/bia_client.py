from bia_integrator_api.util import get_client

from bia_export.settings import Settings

settings = Settings()

api_client = get_client(api_base_url=str(settings.api_base_url))
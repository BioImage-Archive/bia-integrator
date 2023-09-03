from pydantic import BaseSettings
from typing import Optional
from openapi_client.util import simple_client
from openapi_client.api import DefaultApi

class Settings(BaseSettings):
    bia_api_basepath: str = "http://localhost:8080"
    bia_username: Optional[str] = None
    bia_password: Optional[str] = None

    bia_api_client: Optional[DefaultApi] = None

    @property
    def api_client(self) -> DefaultApi:
        if not self.bia_api_client:
            self.bia_api_client = simple_client(
                self.bia_api_basepath,
                self.bia_username,
                self.bia_password
            )
        
        return self.bia_api_client
    
    class Config:
        case_sensitive: True

settings = Settings()
from fastapi import FastAPI

from bia_integrator_core.api import studies
from bia_integrator_core.api import admin

app = FastAPI()
app.include_router(studies.router)
app.include_router(admin.router)

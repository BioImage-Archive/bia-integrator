from api import public
from api import private
from api import auth

from api.models.repository import repository_create, Repository

from fastapi import FastAPI
from typing import AsyncGenerator

from api.api_logging import log_info


async def repository_dependency() -> AsyncGenerator[Repository, None]:
    db = await repository_create(init=False)
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    # Setting this to true results in duplicated client classes (into *Input and *Output) where the api model has default values
    # See https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/#do-not-separate-schemas
    separate_input_output_schemas=False,
    debug=True,
)

app.openapi_version = "3.0.2"

app.include_router(auth.router, prefix="/v2")


@app.on_event("startup")
def on_start():
    log_info("App started")


@app.on_event("shutdown")
def on_start():
    log_info("App stopped")


app.include_router(public.make_router(), prefix="/v2")
app.include_router(private.make_router(), prefix="/v2")

from api import public
from api import private
from api import auth
from api import search
from api.models.repository import repository_create
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from api.api_logging import log_info
import os

from pydantic import ValidationError

app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    # Setting this to true results in duplicated client classes (into *Input and *Output) where the api model has default values
    # See https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/#do-not-separate-schemas
    separate_input_output_schemas=False,
    debug=True,
)

app.openapi_version = "3.0.2"

app.include_router(auth.router, prefix="/v2")


@app.exception_handler(ValidationError)
def remap_validation_error(_, exc: ValidationError):
    """
    This is for Pagination being DI'd with Depends()
    fastapi doesn't have uniform handling of pydantic.ValidationError in that case (default response is a 500)

    See https://github.com/fastapi/fastapi/issues/4974
    """
    return JSONResponse(status_code=422, content={"message": str(exc)})


@app.on_event("startup")
async def on_start():
    if os.getenv("DB_INDEX_REFRESH") == "True":
        # just so "False" / other values don't accidentally trigger indexing
        log_info("App updating indexes")
        await repository_create(push_indices=True)

    log_info("App started")


@app.on_event("shutdown")
def on_shutdown():
    log_info("App stopped")


app.include_router(
    public.make_router(),
    prefix="/v2",
)
app.include_router(
    search.make_router(),
    prefix="/v2",
)
app.include_router(
    private.make_router(),
    prefix="/v2",
    dependencies=[Depends(auth.get_current_user)],
)

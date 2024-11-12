from api.settings import Settings

from api.models.repository import repository_create, Repository


settings = Settings()


async def get_db() -> Repository:
    return await repository_create(settings)


from fastapi import FastAPI, Depends, Request
from api.public import make_router as public_make_router
from api.private import make_router as private_make_router
from api.search import make_router as search_make_router
from api.auth import make_router as auth_make_router, get_current_user
from fastapi.responses import JSONResponse

from api.api_logging import log_info, log_access

from pydantic import ValidationError
import datetime

app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    # Setting this to true results in duplicated client classes (into *Input and *Output) where the api model has default values
    # See https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/#do-not-separate-schemas
    separate_input_output_schemas=False,
    debug=False,
)


@app.middleware("http")
async def custom_access_log(request: Request, call_next):
    start = datetime.datetime.now(datetime.timezone.utc)

    response = await call_next(request)

    end = datetime.datetime.now(datetime.timezone.utc)

    log_access(
        "",
        extra={
            "method": request.method,
            "status": response.status_code,
            "path": request.url.path,
            "response_time_ms": int((end - start).total_seconds() * 1000),
        },
    )
    return response


app.openapi_version = "3.0.2"

app.include_router(auth_make_router(), prefix="/v2")


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
    if settings.mongo_index_push:
        log_info("App updating indexes")

    await repository_create(settings)

    log_info("App started")


@app.on_event("shutdown")
def on_shutdown():
    log_info("App stopped")


app.include_router(
    public_make_router(),
    prefix="/v2",
)
app.include_router(
    search_make_router(),
    prefix="/v2",
)
app.include_router(
    private_make_router(),
    prefix="/v2",
    dependencies=[Depends(get_current_user)],
)

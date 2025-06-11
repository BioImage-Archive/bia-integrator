from api.settings import Settings

from api.models.repository import repository_create, Repository
import asyncio


settings = Settings()


async def get_db() -> Repository:
    event_loop = asyncio.get_event_loop()
    return app.extra["extra"]["event_loop_specific"][event_loop]["db"]


from fastapi import FastAPI, Depends, Request
from api.public import make_router as public_make_router
from api.private import make_router as private_make_router
from api.auth import make_router as auth_make_router, get_current_user
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.api_logging import log_info, log_access

from pydantic import ValidationError
import datetime

app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    # Setting this to true results in duplicated client classes (into *Input and *Output) where the api model has default values
    # See https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/#do-not-separate-schemas
    separate_input_output_schemas=False,
    debug=False,
    root_path=settings.fastapi_root_path,
    extra={"event_loop_specific": {}},
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_methods=["GET"],
    allow_credentials=False,
)


@app.middleware("http")
async def custom_access_log(request: Request, call_next):
    start = datetime.datetime.now(datetime.timezone.utc)

    response = await call_next(request)

    end = datetime.datetime.now(datetime.timezone.utc)

    # ! post body not safe to log
    log_access(
        "",
        extra={
            "method": request.method,
            "status": response.status_code,
            "path": request.url.path,
            # query params ImmutableMultiDict in Starlette - ex for lists
            "query": request.query_params.multi_items(),
            "response_time_ms": int((end - start).total_seconds() * 1000),
            "response_size_bytes": response.headers.get("content-length", None),
            "request_size_bytes": request.headers.get("content-length", None),
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
    event_loop = asyncio.get_event_loop()

    if settings.mongo_index_push:
        log_info("App updating indexes")

    app.extra["extra"]["event_loop_specific"][event_loop] = {
        "db": await repository_create(settings)
    }

    log_info("App started")


@app.on_event("shutdown")
async def on_stop():
    event_loop = asyncio.get_event_loop()
    app.extra["extra"]["event_loop_specific"][event_loop]["db"].connection.close()


@app.on_event("shutdown")
def on_shutdown():
    log_info("App stopped")


app.include_router(
    public_make_router(),
    prefix="/v2",
)
app.include_router(
    private_make_router(),
    prefix="/v2",
    dependencies=[Depends(get_current_user)],
)

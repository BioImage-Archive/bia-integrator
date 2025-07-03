from fastapi import FastAPI, Request
from api.settings import Settings
from api.elastic import Elastic, elastic_create
import asyncio
import datetime
from api.api_logging import log_info, log_access

settings = Settings()
app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    # Setting this to true results in duplicated client classes (into *Input and *Output) where the api model has default values
    # See https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/#do-not-separate-schemas
    separate_input_output_schemas=False,
    debug=False,
    root_path=settings.fastapi_root_path,
    extra={"event_loop_specific": {}},
)


@app.on_event("startup")
async def on_start():
    event_loop = asyncio.get_event_loop()

    app.extra["extra"]["event_loop_specific"][event_loop] = {
        "elastic": await elastic_create(settings),
    }

    log_info("App started")


@app.on_event("shutdown")
async def on_stop():
    event_loop = asyncio.get_event_loop()
    await app.extra["extra"]["event_loop_specific"][event_loop]["elastic"].close()

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


async def get_elastic() -> Elastic:
    event_loop = asyncio.get_event_loop()
    return app.extra["extra"]["event_loop_specific"][event_loop]["elastic"]

from api.website import router as website_router
from api.search import router as search_router

app.include_router(
    search_router
)
app.include_router(
    website_router
)

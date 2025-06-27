from fastapi import FastAPI
from api.settings import Settings
from api.elastic import Elastic, elastic_create
import asyncio
from api.api_logging import log_info

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

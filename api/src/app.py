import os
from dotenv import load_dotenv
load_dotenv(os.environ.get("DOTENV_PATH", None))

from .api import public
from .api import private
from .api import admin
from .api import auth
from .models.repository import repository_create, Repository

import uvicorn
from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.middleware.gzip import GZipMiddleware
import logging

app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    # Setting this to true results in duplicated client classes (into *Input and *Output) where the api model has default values
    # See https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/#do-not-separate-schemas
    separate_input_output_schemas=False,
)

# !!Always explicitly set this
# FastAPI sets version to latest by default (3.1.0 as of this comment)
#   openapi-codegen generates python clients with untyped return values, due to input/output model split in OpenAPI 3.1
# @TODO: Eventually change this, but check (at least) the python client return types not being object
app.openapi_version = "3.0.2"

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(Exception)
async def log_exception_handler(request: Request, exc: Exception): 
    logging.error("Unhandled exception:", exc_info=True)

    return JSONResponse(
        {"detail": "Internal server error"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )

async def repository_dependency() -> Repository:
    db = await repository_create(init = False)
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    await repository_create(init = True)

app.include_router(auth.router, prefix="/api/v1", dependencies=[Depends(repository_dependency)])
app.include_router(private.router, prefix="/api/v1", dependencies=[Depends(repository_dependency)])
app.include_router(admin.router, prefix="/api/v1", dependencies=[Depends(repository_dependency)])
# routes applied in the order they are declared
app.include_router(public.router, prefix="/api/v1", dependencies=[Depends(repository_dependency)])

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    uvicorn.run(app, host="0.0.0.0", port=8080)

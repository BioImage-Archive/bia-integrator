import os
from dotenv import load_dotenv
load_dotenv(os.environ.get("DOTENV_PATH", None))

from .api import public
from .api import private
from .api import admin
from .api import auth

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.middleware.gzip import GZipMiddleware
import logging

app = FastAPI(
    generate_unique_id_function=lambda route: route.name,
    separate_input_output_schemas=False
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(Exception)
async def log_exception_handler(request: Request, exc: Exception): 
    logging.error("Unhandled exception:", exc_info=True)

    return JSONResponse(
        {"detail": "Internal server error"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )

app.include_router(auth.router, prefix="/api/v1")
app.include_router(private.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
# routes applied in the order they are declared
app.include_router(public.router, prefix="/api/v1")

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    uvicorn.run(app, host="0.0.0.0", port=8080)

from . import public
from . import private
from .models.repository import repository_create, Repository


from fastapi import FastAPI
from typing import AsyncGenerator


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

# app.include_router(private.router, prefix="/v2")
# routes applied in the order they are declared
app.include_router(public.router, prefix="/v2")
app.include_router(private.router, prefix="/v2")

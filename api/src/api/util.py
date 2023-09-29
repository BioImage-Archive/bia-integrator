import functools
from fastapi import APIRouter

def model_exclude_id_field(router: APIRouter):
    router.get = functools.partial(router.get, response_model_exclude={"_id", "id"})
    router.post = functools.partial(router.post, response_model_exclude={"_id", "id"})
    router.patch = functools.partial(router.patch, response_model_exclude={"_id", "id"})
    router.put = functools.partial(router.put, response_model_exclude={"_id", "id"})

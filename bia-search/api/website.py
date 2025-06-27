from fastapi import APIRouter, Depends, Query
from typing import Annotated
from api.elastic import Elastic
from api.app import get_elastic

router = APIRouter(prefix="/website")


@router.get("/doc")
async def get_doc(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    uuid: Annotated[str, Query(min_length=1, max_length=500)],
) -> dict:
    rsp = await elastic.client.search(
        index=elastic.index, query={"match": {"uuid": uuid}}, size=1
    )

    return rsp.body["hits"]

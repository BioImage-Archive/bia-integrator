from fastapi import APIRouter, Depends, Query
from typing import Annotated
from api.elastic import Elastic
from api.app import get_elastic

router = APIRouter(
    prefix="/search"
)


@router.get("/fts")
async def fts(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    query: Annotated[str, Query(min_length=1, max_length=500)],
) -> dict:
    rsp = await elastic.client.search(
        index=elastic.index,
        query={
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["*"],
                            "type": "phrase",
                        }
                    },
                    {"simple_query_string": {"query": f"*{query}*", "fields": ["*"]}},
                ]
            }
        },
        size=5,
    )

    return rsp.body["hits"]

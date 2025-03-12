from elasticsearch import AsyncElasticsearch, NotFoundError
from api.settings import Settings


class Elastic:
    client: AsyncElasticsearch

    def __init__(self):
        pass

    async def configure(self, settings: Settings, cleanup=False):
        index_name = "test-index"
        self.client = AsyncElasticsearch(settings.elastic_connstring)

        if cleanup:
            try:
                await self.client.indices.delete(index=index_name)
            except NotFoundError:
                pass

        if not await self.client.indices.exists(index=index_name):
            await self.client.indices.create(
                index="test-index",
                body={
                    "mappings": {
                        "dynamic": False,
                        "properties": {
                            "accession_id": {"type": "keyword"},
                            "author": {"type": "flattened"},
                            "title": {"type": "text"},
                        },
                    }
                },
            )


async def elastic_create(settings: Settings) -> Elastic:
    elastic = Elastic()
    await elastic.configure(settings)

    return elastic

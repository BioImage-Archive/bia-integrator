from elasticsearch import AsyncElasticsearch, NotFoundError
from api.settings import Settings


class Elastic:
    client: AsyncElasticsearch

    def __init__(self):
        pass

    async def configure(self, settings: Settings):
        index_name = "test-index"
        self.client = AsyncElasticsearch(settings.elastic_connstring)

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
                            "dataset": {"type": "flattened"},
                            "description": {"type": "text"},
                        },
                    }
                },
            )

    async def close(self):
        await self.client.close()


async def elastic_create(settings: Settings) -> Elastic:
    elastic = Elastic()
    await elastic.configure(settings)

    return elastic

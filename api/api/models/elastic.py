from elasticsearch import AsyncElasticsearch
from api.settings import Settings


class Elastic:
    client: AsyncElasticsearch

    def __init__(self):
        pass

    async def configure(self, settings: Settings):
        #! if Elastic is used without being configured, exception raised.
        # If never used and not configured, no exception
        #   -> can disable it like a feature flag, and also catch misconfigurations
        if not settings.elastic_connstring:
            self.client = None
            return

        self.client = AsyncElasticsearch(
            settings.elastic_connstring, verify_certs=False
        )
        if not await self.client.indices.exists(index=settings.elastic_index):
            await self.client.indices.create(
                index=settings.elastic_index,
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
        if self.client:
            await self.client.close()


async def elastic_create(settings: Settings) -> Elastic:
    elastic = Elastic()
    await elastic.configure(settings)

    return elastic

from elasticsearch import AsyncElasticsearch
from api.settings import Settings


class Elastic:
    client: AsyncElasticsearch

    def __init__(self):
        pass

    def configure(self, settings: Settings):
        self.client = AsyncElasticsearch(settings.elastic_connstring)


async def elastic_create(settings: Settings) -> Elastic:
    elastic = Elastic()
    elastic.configure(settings)

    return elastic

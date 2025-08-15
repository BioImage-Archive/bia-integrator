from elasticsearch import AsyncElasticsearch
from api.settings import Settings


class Elastic:
    client: AsyncElasticsearch
    index_study: str
    index_image: str

    def __init__(self):
        pass

    async def configure(self, settings: Settings):
        self.client = AsyncElasticsearch(
            settings.elastic_connstring, verify_certs=False
        )
        self.index_study = settings.elastic_index_study
        self.index_image = settings.elastic_index_image

        if not await self.client.indices.exists(index=self.index_study):
            await self.client.indices.create(
                index=self.index_study,
                body={
                    "mappings": {
                        "dynamic": False,
                        "properties": {
                            "uuid": {"type": "keyword"},
                            "accession_id": {"type": "keyword"},
                            "title": {"type": "text"},
                            "description": {"type": "text"},
                            "funding_statement": {"type": "text"},
                            "keyword": {"type": "keyword"},
                            "author": {"type": "flattened"},
                            "grant": {"type": "flattened"},
                            "dataset": {
                                "type": "object",
                                "properties": {
                                    "biological_entity": {
                                        "type": "object",
                                        "properties": {
                                            "organism_classification": {
                                                "type": "object",
                                                "properties": {
                                                    "scientific_name": {
                                                        "type": "keyword"
                                                    },
                                                    "common_name": {"type": "keyword"},
                                                    "ncbi_id": {"type": "keyword"},
                                                },
                                            }
                                        },
                                    },
                                    "acquisition_process": {
                                        "type": "object",
                                        "properties": {
                                            "imaging_method_name": {"type": "keyword"},
                                        },
                                    },
                                },
                            },
                            "release_date": {"type": "date"},
                        },
                    },
                },
            )

        if not await self.client.indices.exists(index=self.index_image):
            await self.client.indices.create(
                index=self.index_image,
                body={
                    "mappings": {
                        "dynamic": False,
                        "properties": {
                            "uuid": {"type": "keyword"},
                            "representation": {
                                "type": "object",
                                "properties": {"image_format": {"type": "keyword"}},
                            },
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

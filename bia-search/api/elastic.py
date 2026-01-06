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

        embeddings = {
            "type": "object",
            "properties": {
                model_name: {
                    "type": "object",
                    "properties": {
                        "embedding": {
                            "type": "dense_vector",
                            "dims": model_dims,  # Dimension of the vector (384 for all-MiniLM-L6-v2)
                            "index": True,
                            #! quantization (ex images)
                            # "index_options": {
                            #    "type": "int8_hnsw"
                            # }
                            "similarity": "cosine"  # default for sentence embedding models
                        }
                    }
                }
                for (model_name, model_dims) in [
                    ("sentence-transformers/all-MiniLM-L6-v2", 384),
                    ("sentence-transformers/msmarco-distilbert-base-tas-b", 768),
                    ("sentence-transformers/all-roberta-large-v1", 1024)
                ]
            },
        }


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
                            "licence": {"type": "keyword"},
                            "dataset": {
                                "type": "object",
                                "properties": {
                                    "uuid": {"type": "keyword"},
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
                            "embeddings": embeddings
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
                                "properties": {
                                    "image_format": {"type": "keyword"},
                                    "size_x": {"type": "integer"},
                                    "size_y": {"type": "integer"},
                                    "size_z": {"type": "integer"},
                                    "size_c": {"type": "integer"},
                                    "size_t": {"type": "integer"},
                                    "total_size_in_bytes": {"type": "long"},
                                    "voxel_physical_size_x": {"type": "float"},
                                    "voxel_physical_size_y": {"type": "float"},
                                    "voxel_physical_size_z": {"type": "float"},
                                },
                            },
                            "total_physical_size_x": {"type": "float"},
                            "total_physical_size_y": {"type": "float"},
                            "total_physical_size_z": {"type": "float"},
                            "creation_process": {
                                "type": "object",
                                "properties": {
                                    "input_image_uuid": {"type": "keyword"},
                                    "acquisition_process": {
                                        "type": "object",
                                        "properties": {
                                            "imaging_method_name": {"type": "keyword"},
                                        },
                                    },
                                    "subject": {
                                        "type": "object",
                                        "properties": {
                                            "sample_of": {
                                                "type": "object",
                                                "properties": {
                                                    "biological_entity_description": {
                                                        "type": "keyword"
                                                    },
                                                    "organism_classification": {
                                                        "type": "object",
                                                        "properties": {
                                                            "scientific_name": {
                                                                "type": "keyword"
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
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

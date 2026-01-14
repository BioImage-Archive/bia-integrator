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
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "default": {"type": "whitespace"},
                                "analyzerCaseInsensitive": {
                                    "tokenizer": "whitespace",
                                    "filter": ["lowercase"],
                                },
                            },
                            "normalizer": {
                                "lowercase_norm": {
                                    "type": "custom",
                                    "filter": ["lowercase"],
                                }
                            },
                        }
                    },
                    "mappings": {
                        "dynamic": False,
                        "properties": {
                            "uuid": {"type": "keyword"},
                            "accession_id": {
                                "type": "keyword",
                                "normalizer": "lowercase_norm",
                            },
                            "title": {
                                "type": "text",
                                "analyzer": "analyzerCaseInsensitive",
                            },
                            "description": {
                                "type": "text",
                                "analyzer": "analyzerCaseInsensitive",
                            },
                            "funding_statement": {
                                "type": "text",
                                "analyzer": "analyzerCaseInsensitive",
                            },
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
                                                        "type": "keyword",
                                                        "normalizer": "lowercase_norm",
                                                    },
                                                    "common_name": {
                                                        "type": "keyword",
                                                        "normalizer": "lowercase_norm",
                                                    },
                                                    "ncbi_id": {"type": "keyword"},
                                                },
                                            }
                                        },
                                    },
                                    "acquisition_process": {
                                        "type": "object",
                                        "properties": {
                                            "imaging_method_name": {
                                                "type": "keyword",
                                                "normalizer": "lowercase_norm",
                                            }
                                        },
                                    },
                                    "annotation_process": {
                                        "type": "object",
                                        "properties": {
                                            "method_type": {
                                                "type": "keyword",
                                                "normalizer": "lowercase_norm",
                                            }
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
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "default": {"type": "whitespace"},
                                "analyzerCaseInsensitive": {
                                    "tokenizer": "whitespace",
                                    "filter": ["lowercase"],
                                },
                            },
                            "char_filter": {
                                "replace_file_format": {
                                    "type": "pattern_replace",
                                    "pattern": "^\\.",
                                    "replacement": "",
                                }
                            },
                            "normalizer": {
                                "lowercase_norm": {
                                    "type": "custom",
                                    "filter": ["lowercase"],
                                },
                                "file_format_norm": {
                                    "type": "custom",
                                    "char_filter": ["replace_file_format"],
                                    "filter": ["lowercase"],
                                },
                            },
                        }
                    },
                    "mappings": {
                        "dynamic": False,
                        "properties": {
                            "uuid": {"type": "keyword"},
                            "total_physical_size_x": {"type": "float"},
                            "total_physical_size_y": {"type": "float"},
                            "total_physical_size_z": {"type": "float"},
                            "representation": {
                                "type": "object",
                                "properties": {
                                    "image_format": {
                                        "type": "keyword",
                                        "normalizer": "file_format_norm",
                                    },
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
                            "creation_process": {
                                "type": "object",
                                "properties": {
                                    "input_image_uuid": {"type": "keyword"},
                                    "acquisition_process": {
                                        "type": "object",
                                        "properties": {
                                            "imaging_method_name": {
                                                "type": "keyword",
                                                "normalizer": "lowercase_norm",
                                            }
                                        },
                                    },
                                    "subject": {
                                        "type": "object",
                                        "properties": {
                                            "sample_of": {
                                                "type": "object",
                                                "properties": {
                                                    "biological_entity_description": {
                                                        "type": "text",
                                                        "analyzer": "analyzerCaseInsensitive",
                                                    },
                                                    "organism_classification": {
                                                        "type": "object",
                                                        "properties": {
                                                            "common_name": {
                                                                "type": "text",
                                                                "analyzer": "analyzerCaseInsensitive",
                                                            },
                                                            "ncbi_id": {
                                                                "type": "keyword"
                                                            },
                                                            "scientific_name": {
                                                                "type": "keyword",
                                                                "normalizer": "lowercase_norm",
                                                            },
                                                        },
                                                    },
                                                },
                                            }
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            )

    async def close(self):
        if self.client:
            await self.client.close()


async def elastic_create(settings: Settings) -> Elastic:
    elastic = Elastic()
    await elastic.configure(settings)

    return elastic

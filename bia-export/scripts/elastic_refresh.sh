#!/bin/bash
set -ex
set -o pipefail

SCRIPT_DIR="$(dirname "$0")"
#API_BASE_URL=${API_BASE_URL:-"http://localhost/api"}
API_BASE_URL=${API_BASE_URL:-"https://wwwdev.ebi.ac.uk/bioimage-archive/api"}
EXPORT_JSON_OUT_DIR=${EXPORT_JSON_OUT_DIR:-"/tmp/"}
ELASTIC_URL=${ELASTIC_URL:-"http://localhost:9200"}
ELASTIC_USERNAME=${ELASTIC_USERNAME:-"elastic"}
ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-"test"}
ELASTIC_INDEX=${ELASTIC_INDEX:-"test_index"}
ELASTIC_INDEX_IMAGES=${ELASTIC_INDEX_IMAGES:-"${ELASTIC_INDEX}_images"}
EXPORT_WORKERS=${EXPORT_WORKERS:-8}

# Export studies and images
poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website all --out_dir=$EXPORT_JSON_OUT_DIR --workers $EXPORT_WORKERS --bulk-gzip

# Delete study Index
curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X DELETE "${ELASTIC_URL}/${ELASTIC_INDEX}"

# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html
# Limit of total fields [1000] in index [test_index] has been exceeded
# also https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html for indexing nested objects
#   either explicitly indexed or flattened?

# Create study index
curl -k -X PUT "${ELASTIC_URL}/${ELASTIC_INDEX}" \
	-u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
	-H "Content-Type: application/json" \
	-d '{
		"settings": {
			"analysis": {
				"analyzer": {
					"default": { "type": "whitespace" },
					"analyzerCaseInsensitive": {
						"tokenizer": "whitespace",
						"filter": ["lowercase"]
					},
					"analyzerStandard": {
						"tokenizer": "standard",
						"filter": ["lowercase"]
					}
				},
				"char_filter": {
					"replace_annotation_type": {
						"type": "pattern_replace",
						"pattern": "_",
						"replacement": " "
					}
				},
				"normalizer": {
					"lowercase_norm": {
						"type": "custom",
						"filter": ["lowercase"]
					},
					"annotation_type_norm": {
						"type": "custom",
						"char_filter": ["replace_annotation_type"],
						"filter": ["lowercase"]
					}
				}
			}
		},
		"mappings": {
			"dynamic": false,
			"properties": {
				"uuid": {
					"type": "keyword"
				},
				"accession_id": {
					"type": "keyword", "normalizer": "lowercase_norm" 
				},
				"title": {
					"type": "text", "analyzer": "analyzerCaseInsensitive"
				},
				"description": {
					"type": "text", "analyzer": "analyzerCaseInsensitive"
				},
				"funding_statement": {
					"type": "text", "analyzer": "analyzerCaseInsensitive"
				},
				"keyword": {
					"type": "keyword", "doc_values": "false"
				},
				"acknowledgement": { "type": "text", "analyzer": "analyzerStandard" },
				"author": {
					"type": "nested",
					"dynamic": false,
					"properties": {
						"display_name": { "type": "text", "analyzer": "analyzerCaseInsensitive" },
						"orcid": {"type": "keyword", "doc_values": "false"},
						"rorid": {"type": "keyword", "doc_values": "false"},
						"affiliation": {
							"type": "nested",
							"dynamic": false,
							"properties": {
								"display_name": { "type": "keyword", "normalizer": "lowercase_norm", "doc_values": "false" },
								"rorid": {"type": "keyword", "doc_values": "false"}
							}
						}
					}
				},
				"grant": {
					"type": "flattened"
				},
				"licence": {"type": "keyword"},
				"dataset": {
					"type": "object",
					"properties": {
						"uuid": { "type": "keyword", "doc_values": "false" },
						"example_image_uri": {"type": "keyword", "index": "false", "doc_values": "true"},
						"biological_entity": {
							"type": "object",
							"properties": {
								"organism_classification": {
									"type": "object",
									"properties": {
										"scientific_name": {
											"type": "text", 
											"analyzer": "analyzerCaseInsensitive",
											"fields": {
												"keyword": { "type": "keyword", "normalizer": "lowercase_norm" }
											}
										},
										"common_name": { "type": "text", "analyzer": "analyzerCaseInsensitive" },
										"ncbi_id": { "type": "keyword", "doc_values": "false" }
									}
								}
							}
						},
						"acquisition_process": {
							"type": "object",
							"properties": {
								"imaging_method_name": {
									"type": "text", 
									"analyzer": "analyzerCaseInsensitive",
									"fields": {
										"keyword": { "type": "keyword", "normalizer": "lowercase_norm" }
									}
								}
							}
						},
						"annotation_process" : {
							"type": "object",
							"properties": {
								"method_type": {
									"type": "text", 
									"analyzer": "analyzerCaseInsensitive",
									"fields": {
										"keyword": { "type": "keyword", "normalizer": "annotation_type_norm" }
									}
								}
							}
						}
					}
				},
				"release_date": {
					"type": "date"
				}
			}
		}
	}'


# Ingest Study data
for f in ${EXPORT_JSON_OUT_DIR}api-study-metadata.bulk.part-*.ndjson.gz; do
  	echo "Uploading $f"
  	gzip -dc "$f" | \
  	curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
    	-H "Content-Type: application/x-ndjson" \
    	-XPOST "${ELASTIC_URL}/_bulk?pretty&error_trace=true" \
    	--data-binary @- | jq '.items[] | select(.index.status != 201)'
	rm -rf $f

done
curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "${ELASTIC_URL}/${ELASTIC_INDEX}/_refresh"

# Delete Image index
curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X DELETE "${ELASTIC_URL}/${ELASTIC_INDEX_IMAGES}"
# Create Image index
curl -k -X PUT "${ELASTIC_URL}/${ELASTIC_INDEX_IMAGES}" \
	-u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
	-H "Content-Type: application/json" \
	-d '{
	"settings": {
		"analysis": {
			"analyzer": {
				"default": { "type": "standard" },
				"analyzerCaseInsensitive": {
					"tokenizer": "standard",
					"filter": ["lowercase"]
				}
			},
			"char_filter": {
				"replace_file_format": {
					"type": "pattern_replace",
					"pattern": "^\\.",
					"replacement": ""
				},
				"replace_annotation_type": {
						"type": "pattern_replace",
						"pattern": "_",
						"replacement": " "
				}
			},
			"normalizer": {
				"lowercase_norm": {
					"type": "custom",
					"filter": ["lowercase"]
				},
				"file_format_norm": {
					"type": "custom",
          			"char_filter": ["replace_file_format"],
					"filter": ["lowercase"]
				},
				"annotation_type_norm": {
						"type": "custom",
						"char_filter": ["replace_annotation_type"],
						"filter": ["lowercase"]
				}
			}
		}
	},
    "mappings": {
        "dynamic": false,
        "properties": {
            "uuid": {
                "type": "keyword"
            },
			"accession_id": { "type": "keyword", "normalizer": "lowercase_norm"},
			"total_physical_size_x": {"type": "float"},
			"total_physical_size_y": {"type": "float"},
			"total_physical_size_z": {"type": "float"},
            "representation": {
                "type": "object",
                "properties": {
                    "image_format": { "type": "keyword", "normalizer": "file_format_norm"},
					"size_x": {"type": "integer"},
					"size_y": {"type": "integer"},
					"size_z": {"type": "integer"},
					"size_c": {"type": "integer"},
					"size_t": {"type": "integer"},
					"total_size_in_bytes": {"type": "long"},
					"voxel_physical_size_x": {"type": "float"},
					"voxel_physical_size_y": {"type": "float"},
					"voxel_physical_size_z": {"type": "float"}
                }
            },
			"creation_process": {
				"type": "object",
				"properties": {
					"input_image_uuid": { "type": "keyword", "doc_values": "false" },
					"acquisition_process": {
						"type": "object",
						"properties": {
							"imaging_method_name": { 
								"type": "text", 
								"analyzer": "analyzerCaseInsensitive",
								"fields": { "keyword": { "type": "keyword", "normalizer": "lowercase_norm" } }
							}
						}
					},
					"annotation_method": {
						"type": "object",
						"properties": {
							"method_type": { 
								"type": "text", 
								"analyzer": "analyzerCaseInsensitive",
								"fields": { "keyword": { "type": "keyword", "normalizer": "annotation_type_norm" } }
							}
						}
					},
					"subject": {
						"type": "object",
						"properties": {
							"sample_of": {
								"type": "object",
								"properties": {
									"biological_entity_description": { "type": "text", "analyzer": "analyzerCaseInsensitive" },
									"organism_classification": {
										"type": "object",
										"properties": {
											"common_name": { "type": "text", "analyzer": "analyzerCaseInsensitive"},
											"ncbi_id": { "type": "keyword", "doc_values": "false" },
											"scientific_name": { 
												"type": "text", 
												"analyzer": "analyzerCaseInsensitive",
												"fields": {
													"keyword": { "type": "keyword", "normalizer": "lowercase_norm" }
												}
											}			
										}
									}
								}
							}
						}
					}
				}
			}
        }
    }
}'
# Ingest Image data
for f in ${EXPORT_JSON_OUT_DIR}api-image-metadata.bulk.part-*.ndjson.gz; do
  	echo "Uploading $f"
  	gzip -dc "$f" | \
  	curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
		-H "Content-Type: application/x-ndjson" \
		-XPOST "${ELASTIC_URL}/_bulk?pretty&error_trace=true" \
		--data-binary @- | jq '.items[] | select(.index.status != 201)'
	rm -rf $f
done

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "${ELASTIC_URL}/${ELASTIC_INDEX_IMAGES}/_refresh"

echo -e "\n\n==============================================\nIndex Status:\n"

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X GET "${ELASTIC_URL}/_cat/indices?v&s=store.size:desc" -H "Content-Type: application/json"
echo ""

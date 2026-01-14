#!/bin/bash
set -ex
set -o pipefail

SCRIPT_DIR="$(dirname "$0")"
API_BASE_URL=${API_BASE_URL:-"http://localhost/api"}
EXPORT_JSON_OUT_FILE=${EXPORT_JSON_OUT_FILE:-"/tmp/api_elastic_refresh.json"}
ELASTIC_URL=${ELASTIC_URL:-"http://localhost:9200"}
ELASTIC_USERNAME=${ELASTIC_USERNAME:-"elastic"}
ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-"test"}
ELASTIC_INDEX=${ELASTIC_INDEX:-"test_index"}
ELASTIC_INDEX_IMAGES=${ELASTIC_INDEX_IMAGES:-"${ELASTIC_INDEX}_images"}

# Export studies
poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website study --out_file=$EXPORT_JSON_OUT_FILE

jq -c 'to_entries | map(.value)[:1000000][] | ({"index": {"_index": "'"${ELASTIC_INDEX}"'"}}, .)' $EXPORT_JSON_OUT_FILE > ${EXPORT_JSON_OUT_FILE}.bulk

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X DELETE "${ELASTIC_URL}/${ELASTIC_INDEX}"

# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html
# Limit of total fields [1000] in index [test_index] has been exceeded
# also https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html for indexing nested objects
#   either explicitly indexed or flattened?
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
					}
				},
				"normalizer": {
					"lowercase_norm": {
						"type": "custom",
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
					"type": "keyword"
				},
				"author": {
					"type": "flattened"
				},
				"grant": {
					"type": "flattened"
				},
				"licence": {"type": "keyword"},
				"dataset": {
					"type": "object",
					"properties": {
						"uuid": { "type": "keyword" },
						"biological_entity": {
							"type": "object",
							"properties": {
								"organism_classification": {
									"type": "object",
									"properties": {
										"scientific_name": {
											"type": "keyword", "normalizer": "lowercase_norm" 
										},
										"common_name": {
											"type": "keyword", "normalizer": "lowercase_norm" 
										},
										"ncbi_id": {
											"type": "keyword"
										}
									}
								}
							}
						},
						"acquisition_process": {
							"type": "object",
							"properties": {
								"imaging_method_name": {
									"type": "keyword", "normalizer": "lowercase_norm" 
								}
							}
						},
						"annotation_process" : {
							"type": "object",
							"properties": {
								"method_type": {
									"type": "keyword", "normalizer": "lowercase_norm" 
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

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
	-H  "Content-Type: application/x-ndjson" \
	-XPOST "${ELASTIC_URL}/_bulk?pretty&error_trace=true" \
	--data-binary @${EXPORT_JSON_OUT_FILE}.bulk | jq '.items[] | select(.index.status != 201)'
curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "${ELASTIC_URL}/${ELASTIC_INDEX}/_refresh"

# Export images
rm -rf $EXPORT_JSON_OUT_FILE

poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website image --out_file=$EXPORT_JSON_OUT_FILE

jq -c 'to_entries | map(.value)[:1000000][] | ({"index": {"_index": "'"${ELASTIC_INDEX_IMAGES}"'"}}, .)' $EXPORT_JSON_OUT_FILE > ${EXPORT_JSON_OUT_FILE}.bulk

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X DELETE "${ELASTIC_URL}/${ELASTIC_INDEX_IMAGES}"

curl -k -X PUT "${ELASTIC_URL}/${ELASTIC_INDEX_IMAGES}" \
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
				}
			},
			"char_filter": {
				"replace_file_format": {
					"type": "pattern_replace",
					"pattern": "^\\.",
					"replacement": ""
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
					"input_image_uuid": { "type": "keyword" },
					"acquisition_process": {
						"type": "object",
						"properties": {
							"imaging_method_name": { "type": "keyword", "normalizer": "lowercase_norm" }
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
											"ncbi_id": { "type": "keyword" },
											"scientific_name": { "type": "keyword", "normalizer": "lowercase_norm" }
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

split -l 5000 ${EXPORT_JSON_OUT_FILE}.bulk ${EXPORT_JSON_OUT_FILE}_bulk_part_

for f in ${EXPORT_JSON_OUT_FILE}_bulk_part_*; do
  echo "Uploading $f"
  curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
       -H "Content-Type: application/x-ndjson" \
       -XPOST "${ELASTIC_URL}/_bulk?pretty&error_trace=true" \
       --data-binary "@$f" | jq '.items[] | select(.index.status != 201)'
  rm -rf $f
done

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "${ELASTIC_URL}/${ELASTIC_INDEX_IMAGES}/_refresh"

echo -e "\n\n==============================================\nIndex Status: ${ELASTIC_INDEX}\n"

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X GET "${ELASTIC_URL}/${ELASTIC_INDEX}/_count" -H "Content-Type: application/json"
echo ""
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

poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website study --out_file=$EXPORT_JSON_OUT_FILE

jq -c 'to_entries | map(.value)[:1000000][] | ({"index": {"_index": "'"${ELASTIC_INDEX}"'"}}, .)' $EXPORT_JSON_OUT_FILE | sed 's/"\./\"A./g' > ${EXPORT_JSON_OUT_FILE}.bulk

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X DELETE "${ELASTIC_URL}/${ELASTIC_INDEX}"

# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html
# Limit of total fields [1000] in index [test_index] has been exceeded
# also https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html for indexing nested objects
#   either explicitly indexed or flattened?
curl -k -X PUT "${ELASTIC_URL}/${ELASTIC_INDEX}" \
	-u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
	-H "Content-Type: application/json" \
	-d '{
		"mappings": {
			"dynamic": false,
			"properties": {
				"uuid": {
					"type": "keyword"
				},
				"accession_id": {
					"type": "keyword"
				},
				"title": {
					"type": "text"
				},
				"description": {
					"type": "text"
				},
				"funding_statement": {
					"type": "text"
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
										"common_name": {
											"type": "keyword"
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
									"type": "keyword"
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

echo -e "\n\n==============================================\nIndex Status: ${ELASTIC_INDEX}\n"

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X GET "${ELASTIC_URL}/${ELASTIC_INDEX}/_count" -H "Content-Type: application/json"
echo ""
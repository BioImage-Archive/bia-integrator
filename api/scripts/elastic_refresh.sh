#!/bin/bash
set -ex

SCRIPT_DIR="$(dirname "$0")"
API_BASE_URL=${API_BASE_URL:-"http://localhost/api/v2"}
EXPORT_JSON_OUT_FILE=${EXPORT_JSON_OUT_FILE:-"/tmp/api_elastic_refresh.json"}
ELASTIC_URL=${ELASTIC_URL:-"http://127.0.0.1:9200"}
ELASTIC_USERNAME=${ELASTIC_USERNAME:-"elastic"}
ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-"test"}
ELASTIC_INDEX=${ELASTIC_INDEX:-"test_index"}

poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website study --out_file=$EXPORT_JSON_OUT_FILE
  
jq -c 'to_entries | map(.value)[:1000000][] | ({"index": {"_index": "'"${ELASTIC_INDEX}"'"}}, .)' $EXPORT_JSON_OUT_FILE | sed 's/"\./\"A./g' > ${EXPORT_JSON_OUT_FILE}.bulk

curl -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X DELETE "${ELASTIC_URL}/${ELASTIC_INDEX}"

# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html
# Limit of total fields [1000] in index [test_index] has been exceeded
# also https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html for indexing nested objects
#   either explicitly indexed or flattened?
curl -X PUT "${ELASTIC_URL}/${ELASTIC_INDEX}" \
	-u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
	-H "Content-Type: application/json" \
	-d '{
	"mappings": {
		"dynamic": false,
		"properties": {
			"accession_id": {
				"type": "keyword"
			},
			"author": {
				"type": "flattened"
			}
		}
	}
}'

curl -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" \
	-H  "Content-Type: application/x-ndjson" \
	-XPOST "${ELASTIC_URL}/_bulk?pretty&error_trace=true" \
	--data-binary @${EXPORT_JSON_OUT_FILE}.bulk | jq '.items.[] | select(.index.status != 201)'
curl -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "${ELASTIC_URL}/${ELASTIC_INDEX}/_refresh"

echo -e "\n\n==============================================\nIndex Status: ${ELASTIC_INDEX}\n"

curl -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X GET "${ELASTIC_URL}/${ELASTIC_INDEX}/_count" -H "Content-Type: application/json"
echo ""
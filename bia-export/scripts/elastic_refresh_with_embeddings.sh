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
# poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website study --embed --out_file=$EXPORT_JSON_OUT_FILE \
#     S-BIAD1159 \
#     S-BIAD2245 \
#     S-BSST445 \
#     S-BIAD1823 \
#     S-BIAD1827 \
#     S-BIAD1839 \
#     S-BIAD1659 \
#     S-BIAD1582 \
#     S-BIAD1842
poetry --directory ${SCRIPT_DIR}/../../bia-export run bia-export website study --embed --out_file=$EXPORT_JSON_OUT_FILE


cp /tmp/api_elastic_refresh.json ./bia-search/api/tests/test_data/bia-study-metadata.json
cd /home/liviu/Documents/bia-integrator/bia-search/api/tests/test_data && jq -c 'to_entries | map(.value)[:10000][] | ({"index": {"_index": "test_index"}}, .)' bia-study-metadata.json \
    > bia-study-metadata.json.bulk
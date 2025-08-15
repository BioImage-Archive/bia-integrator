## To (re)generate test fixtures

```bash
curl -X DELETE "http://localhost:9200/test_index"

# Limit of total fields [1000] in index [test_index] has been exceeded 
curl -X PUT "http://localhost:9200/test_index" \
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
			},
			"dataset": {
				"type": "flattened"
			},
            "title": {
                "type": "text"
            },
			"description": {
				"type": "text"
			}
		}
	}
}'

# run a few times
#? workaround for --directory not working
#poetry --directory=../../../../bia-export run bia-export website study S-BIAD1466 S-BIAD1553
(cd ../../../../bia-export && poetry run bia-export website study --out_file=../bia-search/api/tests/test_data/bia-study-metadata.json S-BIAD1466 S-BIAD1553 S-BIAD1556 S-BIAD1495 S-BIAD1494)

jq -c 'to_entries | map(.value)[:10000][] | ({"index": {"_index": "test_index"}}, .)' bia-study-metadata.json \
    > bia-study-metadata.json.bulk

curl -H "Content-Type: application/x-ndjson" -XPOST 'localhost:9200/_bulk?pretty&error_trace=true' --data-binary @bia-study-metadata.json.bulk | jq '.items.[] | select(.index.status != 201)'



jq -c 'to_entries | map(.value)[:10000][] | ({"index": {"_index": "test_index_images"}}, .)' bia-image-metadata.json \
    > bia-image-metadata.json.bulk

curl -H "Content-Type: application/x-ndjson" -XPOST 'localhost:9200/_bulk?pretty&error_trace=true' --data-binary @bia-image-metadata.json.bulk | jq '.items.[] | select(.index.status != 201)'
```
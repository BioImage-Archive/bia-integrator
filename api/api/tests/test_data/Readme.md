## To (re)generate test fixtures

```bash
curl -X DELETE "http://localhost:9200/test-index"

# Limit of total fields [1000] in index [test_index] has been exceeded 
curl -X PUT "http://localhost:9200/test-index" \
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
            "title": {
                "type": "text"
            }
		}
	}
}'

# run a few times
#? workaround for --directory not working
#poetry --directory=../../../../bia-export run bia-export website study S-BIAD1078 S-BIAD1556
(cd ../../../../bia-export && poetry run bia-export website study --out_file=../api/api/tests/test_data/bia-study-metadata.json S-BIAD1078 S-BIAD1556)

jq -c 'to_entries | map(.value)[:10000][] | ({"index": {"_index": "test-index"}}, .)' bia-study-metadata.json \
    > bia-study-metadata.json.bulk

curl -H "Content-Type: application/x-ndjson" -XPOST 'localhost:9200/_bulk?pretty&error_trace=true' --data-binary @bia-study-metadata.json.bulk | jq '.items.[] | select(.index.status != 201)'
```
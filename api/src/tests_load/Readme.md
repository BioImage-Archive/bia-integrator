! Always get fixtures in on_start (or generally outside of tasks), so the time to get them doesn't count for the actual request
As good practise, copy parameters passed from test_config just to make them obvious/documented. Actual tasks should only use attributes of `self`

Tests are split per-usecase because the max users accepted are very different

## Run everything
```sh
TEST_ENV=local

# create_fixtures
for test_name in get_study_assets mass_update small_get batch_insert; do
    poetry run locust --config=${test_name}/${TEST_ENV}.conf --run-time 5m --headless --html ~/Documents/api_load_tests/${TEST_ENV}/${test_name}.html
    sleep 30 # let db catch up
done
```

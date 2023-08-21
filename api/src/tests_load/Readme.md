poetry run locust --config=bulk_create/local.conf

! Always get fixtures in on_start (or generally outside of tasks), so the time to get them doesn't count for the actual request
As good practise, copy parameters passed from test_config just to make them obvious/documented. Actual tasks should only use attributes of `self`
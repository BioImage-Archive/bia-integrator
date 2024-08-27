Minimal examples for api functionality. Depends on a local api being up.

The examples usually take a "one of each" approach, to avoid making them too verbose. The api and api client generally reflect what is in the models, so if the examples only show "get/create study", but an ImageAnnotationDataset is known to exist in the models, it's safe to assume that "get/create ImageAnnotationDataset" works in the same way. 

The client module **relies heavily on autocomplete / editor suggestions**.

Install dependencies for the example project: `poetry install --no-root`

Run the private_api.py example: `poetry run python private_api.py`
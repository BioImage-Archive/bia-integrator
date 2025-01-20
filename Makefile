.PHONY: api.version client.generate bia-export.test

api.version:
	@echo $(shell grep '^version =' api/pyproject.toml | awk -F\" '{print $$2}')

# no jq in openapi-codegen image
#	so keep original file but make a pretty-printed version too
client.generate:
	MY_UID=$(shell id -u) docker compose --profile codegen up --build --force-recreate --remove-orphans --abort-on-container-exit
	jq '.' $(CURDIR)/clients/openapi.json > $(CURDIR)/clients/openapi_pretty.json

client.examples:
	docker compose --profile client_examples up --build --force-recreate --remove-orphans --abort-on-container-exit


# Note that the github CI is set up to expect Make commands for testing of the form: make ${{matrix.project}}.test
bia-export.test:
	docker compose --profile export_test up --build --force-recreate --remove-orphans --abort-on-container-exit
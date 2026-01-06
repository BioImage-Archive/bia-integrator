.PHONY: $(MAKECMDGOALS)

api.version:
	@echo $(shell grep '^version =' api/pyproject.toml | awk -F\" '{print $$2}')

# no jq in openapi-codegen image
#	so keep original file but make a pretty-printed version too
client.generate:
	MY_UID=$(shell id -u) docker compose --profile codegen up --build --force-recreate --remove-orphans --abort-on-container-exit
	jq '.' $(CURDIR)/clients/openapi.json > $(CURDIR)/clients/openapi_pretty.json

client.examples:
	docker compose --profile client_examples up --build --force-recreate --remove-orphans --abort-on-container-exit

client.search.generate:
	MY_UID=$(shell id -u) docker compose --profile codegen_search up --build --force-recreate --remove-orphans --abort-on-container-exit
	jq '.' $(CURDIR)/clients/search/openapi.json > $(CURDIR)/clients/search/openapi_pretty.json

api.up:
	docker compose up -d --build --wait

api.down:
	docker compose down

search.up:
	docker compose --profile search up -d --build --wait --force-recreate --remove-orphans

search.down:
	docker compose down

-include Makefile.local
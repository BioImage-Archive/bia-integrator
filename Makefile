.PHONY: api.version client.generate api.up api.down

api.version:
	@echo $(shell grep '^version =' api/pyproject.toml | awk -F\" '{print $$2}')

# no jq in openapi-codegen image
#	so keep original file but make a pretty-printed version too
client.generate:
	MY_UID=$(shell id -u) docker compose --profile codegen up --build --force-recreate --remove-orphans --abort-on-container-exit
	jq '.' $(CURDIR)/clients/openapi.json > $(CURDIR)/clients/openapi_pretty.json

client.examples:
	docker compose --profile client_examples up --build --force-recreate --remove-orphans --abort-on-container-exit

api.up:
 	docker compose up -d --build --wait

api.down:
	docker compose down

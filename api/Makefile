.PHONY: api.version

api.version:
	@echo $(shell grep 'version =' pyproject.toml | awk -F\" '{print $$2}')


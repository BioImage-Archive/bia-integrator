.PHONY: version

api.version:
	@echo $(shell grep 'version =' api/pyproject.toml | awk -F\" '{print $$2}')


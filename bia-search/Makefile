VERSION := $(shell grep '^version =' pyproject.toml | awk -F\" '{print $$2}')

.PHONY: api.version api.push api.refresh

api.version:
	@echo $(VERSION)

api.push:
	docker build ../ -f Dockerfile -t bia-integrator-search
	docker image tag bia-integrator-search ghcr.io/bioimage-archive/bia-integrator-search:$(VERSION)
	docker image push ghcr.io/bioimage-archive/bia-integrator-search:$(VERSION)

api.refresh: api.push
	@echo "Listing search pods..."
	kubectl get pods | grep search-
	@echo "Deleting search pods..."
	kubectl delete pods -l app.kubernetes.io/instance=search
	@echo "Waiting for pods to restart..."
	kubectl wait --for=condition=Ready pods -l app.kubernetes.io/instance=search --timeout=300s

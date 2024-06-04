## Setup

```sh
minikube start --memory=10000 --cpus=4 --extra-config=apiserver.service-node-port-range=1-65535
helm install bia-api-local ./helm-chart -f ./local/api_values.yml
helm test bia-api-local --logs

# cleanup/delete
helm uninstall bia-api-local
minikube delete
```

## Accessing apps

```bash
kubectl port-forward svc/mongo-mongodb 27017:27017
kubectl port-forward svc/api 8080:8080
```

If running the api (or tests) locally for development, the mongo port needs to be forwarded and MONGO_CONNSTRING in .env should point to localhost with the mongo values in `api_values.yml` 
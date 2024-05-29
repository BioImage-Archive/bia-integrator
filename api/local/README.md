## Setup

```sh
minikube start --memory=10000 --cpus=4 --extra-config=apiserver.service-node-port-range=1-65535
```

* `cp .env_template .env`
* helmsman --apply -f helmsman_local.yml -e .env

## Accessing apps

```bash
kubectl port-forward svc/mongo-mongodb 27017:27017
kubectl port-forward svc/api 8080:8080
```
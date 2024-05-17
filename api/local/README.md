## Setup

```sh
minikube start --memory=10000 --cpus=4 --extra-config=apiserver.service-node-port-range=1-65535


# create RO classic token for minikube here https://github.com/settings/tokens
kubectl create secret --namespace api docker-registry ghcr-creds \
    --docker-server=https://ghcr.io \
    --docker-username=GITHUB_USERNAME \
    --docker-password=SEE_COMMENT \
    --docker-email=GITHUB_EMAIL
```

* `cp .env_template .env`
* helmsman --apply -f helmsman_local.yml -e .env

## Accessing apps

```bash
kubectl port-forward svc/mongo-mongodb 27017:27017
kubectl port-forward svc/api 8080:8080
```


### Prerequisites
- Docker (or another container runtime)
- kubectl
- minikube
- Python 3.12+ (for host-side development outside containers)

Versions tested against:
```bash
docker --version
kubectl version --client
minikube version
python3 --version
```

### Run a single service with Docker (development loop)

Useful for fast iteration on one service without spinning up the cluster. No persistence, in-memory storage only.

Build the api-service image:
```bash
cd services/api
docker build -t url-shortener-api:0.1 .
```

Run it:
```bash
docker run --rm -p 8000:8000 url-shortener-api:0.1
```

Test from another terminal:
```bash
# Health check
curl http://localhost:8000/healthz

# Create a short link
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Resolve a short link (use the code returned above)
curl http://localhost:8000/<code>
```

Stop with Ctrl+C. The `--rm` flag in `docker run` removes the container automatically on stop.

### Run the full stack on Kubernetes (deployment target)

Bring up the cluster:
```bash
minikube start
kubectl get nodes
```
Expected: one node, status `Ready`.

#### Cluster smoke test (verify cluster health before deploying app)
Run this whenever something feels broken — confirms scheduling, services, and traffic routing work.

```bash
kubectl create deployment hello-test --image=kicbase/echo-server:1.0
kubectl expose deployment hello-test --type=NodePort --port=8080
kubectl wait --for=condition=available --timeout=60s deployment/hello-test
minikube service hello-test --url
```

Hit the returned URL with `curl` — you should get an echo response.

Clean up:
```bash
kubectl delete deployment hello-test
kubectl delete service hello-test
```

#### Deploy the application
(Manifests will be added as the project develops.)

```bash
#### Deploy the application

Build and load the api-service image into minikube:
```bash
cd services/api
docker build -t url-shortener-api:0.1 .
cd ../..
minikube image load url-shortener-api:0.1
```

Apply the manifests:
```bash
kubectl apply -f manifests/api/
```

Verify:
```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

All deployments should report ready replicas, and pods should show `Running` with status `1/1`.

Access the service via port-forward:
```bash
kubectl port-forward service/api 8080:80
```

In another terminal:
```bash
curl http://localhost:8080/healthz
curl -X POST http://localhost:8080/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Architecture

Three services running on minikube:

- **api** (2 replicas): URL shortener. POST `/shorten` creates a code, GET `/{code}` resolves it and atomically increments a click counter.
- **stats** (2 replicas): Read-only stats service. GET `/stats/{code}` returns click counts for a specific code, GET `/stats` lists all.
- **redis** (1 replica): Shared state. Backed by a 1Gi PVC with appendonly persistence.

Service-to-service communication uses Kubernetes' internal DNS — api and stats reach Redis via the hostname `redis` (which the cluster resolves to the redis Service's ClusterIP, which load-balances to the redis pod).

All services use FastAPI on Python 3.12-slim, with health probes on `/healthz` that include Redis connectivity checks.

**Note:** The api-service runs 2 replicas with in-memory storage, so consecutive requests may hit different pods with inconsistent state. This is intentional and motivates the Redis backing store added in the next iteration.
```

### Setup secrets

This project uses a Kubernetes Secret to store the Redis password. The real Secret manifest (`manifests/config/secret.yaml`) is gitignored — it must be created locally before deploying. A committed template (`manifests/config/secret.yaml.example`) shows the required structure.

To set up:

1. Copy the template:
   \`\`\`bash
   cp manifests/config/secret.yaml.example manifests/config/secret.yaml
   \`\`\`

2. Generate a password:
   \`\`\`bash
   openssl rand -base64 24
   \`\`\`

3. Open `manifests/config/secret.yaml` and replace `<your-password-here>` with the generated password.

4. Apply when deploying:
   \`\`\`bash
   kubectl apply -f manifests/config/
   \`\`\`

**Note on production:** In production, secrets should never be stored as committed YAML files — even with the gitignore protection. Real systems use external secret managers such as HashiCorp Vault, AWS Secrets Manager, or sealed-secrets. The pattern here is acceptable for local learning but not for shared environments.

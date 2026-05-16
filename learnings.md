# Learnings — k8s-multi-service-deploy

## 2026-05-13
Day 1. Toolchain verified: kubectl, minikube, Docker all working. Hello-world deployment + NodePort service routed correctly. Repo scaffolded with five-section README. Next: design the actual services to deploy (decide between echo-service + Redis vs. two-service web app pattern).

## 2026-05-14
Day 2. Built api-service: FastAPI URL shortener with /shorten, /:code, /healthz endpoints. In-memory store for now. Dockerfile based on python:3.12-slim, builds clean, runs locally on port 8000. Decided to include /healthz from day one — K8s liveness probes will need it later. Next: deploy this to minikube (write Deployment + Service manifests).

## 2026-05-15
Day 3. First K8s manifests — Deployment + Service for api-service.
- Loaded local Docker image into minikube via `minikube image load`. imagePullPolicy IfNotPresent prevents trying to fetch from a remote registry.
- Two replicas with in-memory store: requests split across pods, state diverges. Visceral demo of why distributed services need shared state.
- Liveness probe restarts dead pods, readiness probe controls traffic routing. Same /healthz endpoint serves both today.
- Explicit resource requests/limits set; defaults would let pods consume the whole cluster.
Next (Sunday marathon): add Redis with a PVC, refactor api-service to use it, write stats-service.

## 2026-05-16 (Saturday — marathon, swapped with Sunday rest because driving tomorrow)

Full implementation marathon. ~4 hours. Three phases:

1. **Deployed Redis** with a PVC for persistence. Learned the PVC/PV/volumeMount triangle — PVC is the request, PV is the actual storage, volumeMount connects it to a container path. AOF persistence requires writes to /data which is what the PVC backs. Used TCP socket for liveness (Redis has no HTTP) and exec'd `redis-cli ping` for readiness.

2. **Refactored api-service to use Redis.** The architectural payoff was visceral — same test that demonstrated the in-memory split on Day 3 now works perfectly. Used SET NX for atomic code allocation. /healthz now checks Redis too; a health endpoint that doesn't check critical dependencies is theater. Configured via env vars (REDIS_HOST, REDIS_PORT) injected through the Deployment spec — the api pod resolves the hostname "redis" via Kubernetes internal DNS to the Redis Service's ClusterIP. This is service discovery in action.

3. **Wrote stats-service** — read-only, separate concern from api. Used Redis SCAN instead of KEYS (KEYS is O(n) and blocks Redis; SCAN is cursor-based, production-safe). Stats reads `clicks:{code}` keys that api atomically increments via INCR. The two services share state without knowing about each other directly.

Biggest concept of the day: **service discovery via DNS.** The api Deployment just says REDIS_HOST=redis. Kubernetes does the rest. No hardcoded IPs, no config maps with addresses, no service registration code. The Service object's name *is* the discoverable address. This is one of the cleanest things in K8s and it's worth pausing on.

Next session (Monday, Day 4): probably ConfigMaps and Secrets — moving env var config out of the Deployment spec into proper config resources. Then ingress to expose api and stats on hostnames instead of port-forwards. Then observability (Prometheus) somewhere in Week 2-3.

Commit that too (single-line commit message is fine for learnings: Log Day 2 learnings).

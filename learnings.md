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

Commit that too (single-line commit message is fine for learnings: Log Day 2 learnings).

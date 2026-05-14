# Learnings — k8s-multi-service-deploy

## 2026-05-13
Day 1. Toolchain verified: kubectl, minikube, Docker all working. Hello-world deployment + NodePort service routed correctly. Repo scaffolded with five-section README. Next: design the actual services to deploy (decide between echo-service + Redis vs. two-service web app pattern).

## 2026-05-14
Day 2. Built api-service: FastAPI URL shortener with /shorten, /:code, /healthz endpoints. In-memory store for now. Dockerfile based on python:3.12-slim, builds clean, runs locally on port 8000. Decided to include /healthz from day one — K8s liveness probes will need it later. Next: deploy this to minikube (write Deployment + Service manifests).

Commit that too (single-line commit message is fine for learnings: Log Day 2 learnings).

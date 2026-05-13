# k8s-multi-service-deploy
Multi-service Kubernetes deployment with persistent storage, ingress routing, and observability
# k8s-multi-service-deploy

## Problem statement
A multi-service application deployed on Kubernetes, demonstrating service-to-service communication, persistent storage, ingress routing, and basic observability. Built as a hands-on study of operational Kubernetes patterns.

## What the design demonstrates
(To be filled as the project develops. Intended coverage: Deployment and Service primitives, ConfigMaps and Secrets, PersistentVolumeClaims, Ingress with path-based routing, Prometheus metrics scraping.)

## Tech choices
- **Cluster:** minikube (local single-node) — sufficient for learning and demos, swappable for kind or a real cluster.
- **Languages:** TBD per service. Likely Go for one service, Python for another, to demonstrate polyglot service-to-service patterns.
- **Observability:** Prometheus for metrics, kubectl logs for now (revisit Loki later if useful).

## How to run locally
```bash
minikube start
kubectl apply -f manifests/
minikube service <service-name> --url
```
(Manifests will be added as the project develops.)

## What was non-obvious during the build
(Engineering journal entries. To be filled as decisions get made and bugs get debugged.)

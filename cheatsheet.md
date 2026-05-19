# Cheatsheet — k8s-multi-service-deploy

A working reference for commands used in this project, organized by tool. Updated as the project evolves.

---

## Quick index — common tasks

- **Start the day**: `open -a Docker` (wait for whale to stop animating) → `minikube start` → `kubectl get pods` to verify cluster is healthy
- **End the day**: `minikube stop` (preserves PVC data, frees laptop CPU/memory)
- **Deploy a new service**: build image → `minikube image load` → `kubectl apply -f manifests/<service>/`
- **Bump a service to a new image version**: edit Dockerfile/code → `docker build -t <name>:<new-tag>` → `minikube image load` → edit manifest's `image:` line → `kubectl apply`
- **Debug a failing pod**: `kubectl describe pod <name>` → `kubectl logs <name>` → `kubectl logs <name> --previous` if it crashed
- **Service "isn't working"**: check `kubectl get endpoints <service>` first — empty endpoints = label/selector mismatch
- **Test a service from laptop**: `kubectl port-forward service/<name> LOCAL:SERVICE`
- **Debug from inside a container**: `kubectl exec -it <pod> -- /bin/sh`
- **Verify env vars are flowing**: `kubectl exec deployment/<name> -- env | grep <pattern>`
- **Verify storage is working**: `kubectl get pvc` — should show `Bound`
- **Watch logs in real time during testing**: `kubectl logs -f -l app=<service>`
- **Detect image drift**: compare `kubectl get deployment <name> -o jsonpath='{.spec.template.spec.containers[0].image}'` vs the running pod's image
- **Clean up a smoke test**: delete deployment AND service (they don't cascade)

---

## Docker — image lifecycle

| Command | What it does | When used |
|---|---|---|
| `docker --version` | Prints installed Docker version | Day 1 |
| `docker build -t <name>:<tag> .` | Builds an image from the Dockerfile in current directory, labels it `<name>:<tag>`. The `.` is the build context | Day 2, Saturday, Day 5 |
| `docker images` | Lists images in your local Docker registry | Day 2 |
| `docker run -p HOST:CONTAINER <image>` | Starts a container, maps host port to container port | Day 2 |
| `docker run --rm -p ...` | Same as above, but auto-removes the container when it stops | Day 2 |
| `docker ps` | Lists running containers. Empty list (no error) = Docker is up but no containers running | Day 5 |
| `Ctrl+C` (inside running container terminal) | Stops the foreground container | Day 2 |

**Principle:** image tags are version contracts. When image content changes, bump the tag. `latest` hides which version is running — fine for dev, dangerous in production.

---

## Kubernetes / minikube — cluster lifecycle

| Command | What it does | When used |
|---|---|---|
| `minikube version` | Prints minikube version | Day 1 |
| `minikube status` | Reports cluster state (`Running`/`Stopped`). Quick diagnostic when kubectl fails mysteriously | Day 5 |
| `minikube start` | Boots up the local single-node Kubernetes cluster. Requires Docker running | Day 1, Day 3, Day 5 |
| `minikube stop` | Pauses the cluster without destroying it. PVC data preserved on `minikube start` | Saturday |
| `minikube image load <name>:<tag>` | Loads a host Docker image into minikube's internal registry | Day 3, Saturday, Day 5 |
| `minikube image ls` | Lists images visible to minikube | Day 3 |
| `minikube service <name> --url` | Returns URL where a NodePort service is reachable from the host | Day 1 |
| `eval $(minikube docker-env)` | Points your shell's Docker CLI at minikube's Docker daemon | Alternative to `image load` for faster iteration |
| `open -a Docker` (Mac) | Opens Docker Desktop. Required before `minikube start` if Docker isn't auto-started | Day 5 |

---

## kubectl — querying cluster state

| Command | What it does | When used |
|---|---|---|
| `kubectl version --client` | Prints kubectl client version (doesn't contact cluster) | Day 1 |
| `kubectl get nodes` | Lists cluster nodes and their status | Day 1 |
| `kubectl get pods` | Lists pods in the current namespace | Day 1, Day 3, Saturday, Day 5 |
| `kubectl get pods -l <label>=<value>` | Filter pods by label selector | Day 5 |
| `kubectl get deployments` | Lists Deployments and their replica status | Day 3, Saturday, Day 5 |
| `kubectl get services` (or `svc`) | Lists Services with types, ClusterIPs, ports | Day 3, Saturday |
| `kubectl get endpoints` | Lists each Service's current routing targets (pod IPs). **First place to check when a service "isn't working"** | Day 3 |
| `kubectl get configmap <name> -o yaml` | Prints full ConfigMap including `data:` keys. Verifies ConfigMap was applied correctly | Day 5 |
| `kubectl get pvc` | Lists PersistentVolumeClaims and bind status (`Pending`/`Bound`/`Lost`) | Saturday |
| `kubectl get pv` | Lists PersistentVolumes (backing storage PVCs bind to) | Storage debugging |
| `kubectl get all` | Common resource types together — pods, services, deployments, replicasets | Day 3 |
| `kubectl get events --sort-by='.lastTimestamp'` | Recent cluster events in time order — "what broke just now?" | Mentioned Day 3 |
| `kubectl describe pod <name>` | Verbose pod status — events, container state, restart history. **Starting point when a pod is weird** | Day 3 |
| `kubectl describe service <name>` | Verbose service status including current endpoints | Day 3 |
| `kubectl describe deployment <name>` | Verbose deployment status, rollout state, env var sources | Day 5 |
| `kubectl get deployment <name> -o jsonpath='{.spec.template.spec.containers[0].image}'` | Prints the image the Deployment spec is configured to run. Source of truth for what should be running | Day 5 |
| `kubectl get pods -l app=<name> -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'` | Prints each pod's name and the image it's actually running. Compare against Deployment spec to detect drift | Day 5 |

---

## kubectl — logs and observability

| Command | What it does | When used |
|---|---|---|
| `kubectl logs <pod-name>` | Prints stdout/stderr of a pod's container | Day 3 |
| `kubectl logs -f <pod-name>` | Follows logs in real time (like `tail -f`) | Day 3 |
| `kubectl logs <pod-name> --previous` | Logs from previous instance — for debugging crashes after restart | Mentioned Day 3 |
| `kubectl logs --tail=N <pod-name>` | Last N lines only | Day 3 |
| `kubectl logs -l <label>=<value>` | Logs from all pods matching a label selector | Saturday |
| `kubectl logs -f -l app=<service> --max-log-requests=10` | Follow logs across all replicas of a service | Saturday |
| `kubectl logs deployment/<name>` | Logs from the deployment (picks one of its pods) | Saturday |
| `kubectl rollout status deployment/<name>` | Blocks until a deployment rollout completes | Mentioned Day 3 |
| `kubectl rollout history deployment/<name>` | Lists past revisions of a deployment | Mentioned Day 3 |

---

## kubectl — modifying cluster state

| Command | What it does | When used |
|---|---|---|
| `kubectl create deployment <name> --image=<image>` | Imperative deployment creation | Day 1 smoke test |
| `kubectl expose deployment <name> --type=NodePort --port=N` | Imperative service creation | Day 1 smoke test |
| `kubectl apply -f <file-or-directory>` | Declarative — applies a manifest. **The production way.** | Day 3, Saturday, Day 5 |
| `kubectl delete deployment <name>` | Deletes Deployment (cascades to ReplicaSet and Pods, NOT Service) | Day 3 cleanup |
| `kubectl delete service <name>` | Deletes Service. Independent from Deployment lifecycle | Day 3 cleanup |
| `kubectl delete -f <file-or-directory>` | Inverse of apply — removes everything in the manifests | Project teardown |
| `kubectl wait --for=condition=available --timeout=Ns deployment/<name>` | Blocks until a deployment is ready | Day 1 |

**Principle:** prefer `kubectl apply -f` (declarative, version-controlled) over imperative `create`/`expose`. Imperative is fine for one-off smoke tests; manifests are how you actually run things.

---

## kubectl — running inside containers

| Command | What it does | When used |
|---|---|---|
| `kubectl exec -it <pod-name> -- /bin/sh` | Opens interactive shell inside a running container | Saturday |
| `kubectl exec -it <pod-name> -- /bin/bash` | Same, with bash if available | — |
| `kubectl exec -it deployment/<name> -- <command>` | Runs command in a pod of that deployment | Saturday |
| `kubectl exec <pod-name> -- <command>` | Non-interactive one-off command | env-var checks, curl from inside |
| `kubectl exec deployment/<name> -- env \| grep <pattern>` | Verify env vars actually injected into a running pod — confirms ConfigMap and Secret wiring | Day 5 |

**Use case:** `kubectl exec` is how you debug "is the container's view of the world what I think it is" — env vars, files, network reachability from inside.

---

## kubectl — bridging cluster to your laptop

| Command | What it does | When used |
|---|---|---|
| `kubectl port-forward service/<name> LOCAL:SERVICE` | Tunnels local port to a Service. **REMOTE is the Service's `port`, not container port** | Day 3, Saturday, Day 5 |
| `kubectl port-forward pod/<name> LOCAL:CONTAINER` | Tunnels to a specific pod, bypassing Service. **REMOTE is the container's port** | — |
| `kubectl port-forward deployment/<name> LOCAL:CONTAINER` | Same as pod — kubectl picks one of the deployment's pods | — |
| `Ctrl+C` (during port-forward) | Stops the port-forward | Day 3 |

---

## Redis — smoke testing via redis-cli

| Command | What it does |
|---|---|
| `kubectl exec -it deployment/redis -- redis-cli` | Opens Redis CLI inside the Redis pod |
| `PING` | Verifies Redis is responding (returns `PONG`). With auth enabled, returns `(error) NOAUTH Authentication required` until you authenticate |
| `AUTH <password>` | Authenticates the session against the configured password |
| `SET <key> <value>` | Writes a key |
| `GET <key>` | Reads a key |
| `INCR <key>` | Atomically increments an integer value at key. (Used by api-service for click counts) |
| `SCAN <cursor> MATCH <pattern>` | Cursor-based key iteration; production-safe. **`KEYS` is O(n) and blocks Redis — never use it on a large dataset.** Used by stats-service |
| `exit` | Leaves redis-cli |

---

## Secrets — generating values

| Command | What it does | When used |
|---|---|---|
| `openssl rand -base64 24` | Generate cryptographically random 24-byte string, base64-encoded. Used for passwords, tokens, signing keys | Day 5 |

---

## Git — version control

| Command | What it does | When used |
|---|---|---|
| `git clone <url>` | Downloads a remote repo to your machine | Day 1 |
| `git add <files-or-directory>` | Stages changes for commit | Daily |
| `git commit -m "message"` | Records staged changes with a message | Daily |
| `git push` | Uploads commits to GitHub | Daily |
| `git status` | Shows staged, unstaged, and untracked changes | Useful daily |
| `git log --oneline` | Shows recent commits as one-line summaries | Useful for "what did I do recently" |

---

## Shell — file/directory operations

| Command | What it does | When used |
|---|---|---|
| `pwd` | Prints current working directory. Fastest debug for "where am I?" | Day 2 |
| `ls` / `ls -a` | Lists files; `-a` includes hidden files | Day 1, Day 2 |
| `cd <path>` | Change directory | Daily |
| `mkdir -p <path>` | Create directory; `-p` creates parents and doesn't error if exists | Day 2, Day 3, Saturday, Day 5 |
| `cat <file>` | Print file contents | Day 2 |
| `cat > <file> << 'EOF' ... EOF` | Heredoc — creates a file with content between EOF markers | Day 2 |
| `cp <src> <dst>` | Copy a file | Day 5 (secret.yaml.example → secret.yaml) |
| `head -5 <file>` | Print first 5 lines | Day 1 |
| `grep <pattern> <file>` | Search for pattern in file | Day 1, Day 3, Day 5 |
| `curl <url>` | HTTP request from terminal | Daily |
| `curl -X POST <url> -H "Content-Type: application/json" -d '...'` | POST with JSON body | Day 2, Day 3, Saturday |
| `echo "<line>" >> <file>` | Append a line to a file | Day 5 (adding to .gitignore) |
| `open -e <file>` (Mac) | Opens file in TextEdit | Day 2 |

---

## vi — terminal editor

| Command | What it does |
|---|---|
| `vi <file>` | Opens file in vi (command mode) |
| `i` | Enter insert mode |
| `Esc` | Leave insert mode |
| `gg` | Jump to top of file |
| `G` | Jump to end of file |
| `dG` | Delete from current line to end of file |
| `ggdG` | Empty the file |
| `:wq` | Save and quit |
| `:q!` | Quit without saving |
| `u` | Undo last change |

---

## Python — virtual environment

| Command | What it does | When used |
|---|---|---|
| `python3 -m venv .venv` | Creates a Python venv in `.venv/` | Day 2 |
| `source .venv/bin/activate` | Activates venv — prompt prefixes with `(.venv)` | Day 2 and after |
| `which python` | Shows which Python the shell will run | Day 2 |
| `pip install -r requirements.txt` | Installs packages from requirements file | Day 2 |
| `python -c "import X; print(X.__version__)"` | Quick check of a package's version | Day 2 |

---

## Concepts worth re-reading

### From Day 3

1. **Resources are independent in K8s.** Deleting a Deployment does NOT delete its Service. Cascade only goes Deployment → ReplicaSet → Pods, never sideways. Use `kubectl delete -f <manifests-dir>` for symmetric cleanup.

2. **Services are DNS + endpoint-list promises, not pod owners.** The endpoints controller watches pods, finds matches by selector, updates endpoints list. Empty endpoints almost always means a label/selector mismatch — `kubectl get endpoints` is the underrated debugging command.

3. **`imagePullPolicy: IfNotPresent`** makes minikube use locally loaded images instead of pulling from a remote registry.

### From Saturday marathon

4. **Service discovery via DNS.** `REDIS_HOST=redis` works because cluster DNS resolves a Service's name to its ClusterIP. No hardcoded IPs, no service registry. The Service's name *is* the discoverable address.

5. **The persistence triangle: PVC → PV → volumeMount.** PVC is a *request*; PV is the actual storage that fulfills it; `volumeMounts` connects the bound PVC to a path inside the container. All three must align or nothing persists.

6. **Probe choice reflects what the service can answer.** HTTP `/healthz` for HTTP services. TCP socket for services with no HTTP (like Redis). `exec` for command-based checks. Liveness restarts dead pods; readiness controls traffic — same endpoint can serve both with different purposes.

7. **Health checks must reflect real dependencies.** A `/healthz` that returns 200 OK regardless of dependency state is theater. Both api and stats checking Redis is correct because both genuinely depend on it. Extract a shared health-check module at the third service.

8. **Replicas count is a correctness decision for stateful services.** Stateless services scale freely. Redis runs `replicas: 1` because multiple replicas without proper clustering would split state.

9. **Image tags are version contracts.** Bump the tag when content changes. `latest` hides which version is running.

10. **Manifests are the architecture.** The YAML *is* the design doc — reading manifests tells you how the service expects to deploy, scale, monitor, and recover.

### From Day 5

11. **ConfigMaps vs Secrets.** Same shape, different intent. ConfigMap = non-sensitive (hostnames, log levels). Secret = sensitive (passwords, keys). Both consumed via `envFrom:` (bulk) or `*KeyRef:` (per-key with renaming). `envFrom:` accepts multiple sources. **Production caveat:** real secrets do NOT belong in committed YAML — use external secret managers.

12. **The Deployment spec is the source of truth for what runs.** Deleting a pod doesn't roll a new image — it just forces the Deployment to recreate the pod from whatever the spec says. To roll a new image: bump tag → `minikube image load` → edit manifest's `image:` → `kubectl apply`. Manual pod deletion is rarely the right tool.

13. **Service port vs container port.** `containerPort` and `targetPort` are dictated by what the app listens on (Redis: 6379, FastAPI: 8000). The Service's `port` is a free choice but should follow protocol conventions — Redis on 6379, HTTP on 80. This lets clients use defaults.

14. **`kubectl port-forward` target determines what REMOTE port means.** `service/X` → Service's `port`. `pod/X` or `deployment/X` → container's `containerPort`. Forwarding to a Service's `targetPort` fails because the Service isn't listening there.

15. **The `.example` template pattern.** Committed template file with placeholder values that mirrors a gitignored real config. Standard for secrets, env files, local config. Solves "how does someone else deploy this" without leaking values.

16. **Probe tuning fields matter.** `timeoutSeconds` (default 1) is often too tight for exec probes and dependency-checking HTTP probes. `failureThreshold` (default 3) filters transient noise. Defaults are usable but rarely correct.

17. **Operational discipline: when bumping shared dependencies, scan which services need rebuild.** Every consuming service needs code update → image rebuild → image load → manifest tag bump → apply. Easy to miss one when working sequentially.

18. **Misleading kubectl errors.** "Error validating manifest: failed to download openapi" usually means kubectl couldn't reach the cluster at all (port 8080 connection refused), not that the manifest is invalid. First check: `minikube status`.
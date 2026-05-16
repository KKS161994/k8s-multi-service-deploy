# Cheatsheet — k8s-multi-service-deploy

A working reference for commands used in this project, organized by tool. Updated as the project evolves.

---

## Quick index — common tasks

- **Deploy a new service**: build image → `minikube image load` → `kubectl apply -f manifests/<service>/`
- **Debug a failing pod**: `kubectl describe pod <name>` → `kubectl logs <name>` → `kubectl logs <name> --previous` if it crashed
- **Service "isn't working"**: check `kubectl get endpoints <service>` first — empty endpoints = label/selector mismatch
- **Test a service from laptop**: `kubectl port-forward service/<name> LOCAL:SERVICE`
- **Debug from inside a container**: `kubectl exec -it <pod> -- /bin/sh`
- **Verify storage is working**: `kubectl get pvc` — should show `Bound`
- **Watch logs in real time during testing**: `kubectl logs -f -l app=<service>`
- **Clean up a smoke test**: delete deployment AND service (they don't cascade)
- **Bump a service to a new image version**: edit Dockerfile/code → `docker build -t <name>:<new-tag>` → `minikube image load` → edit manifest's `image:` line → `kubectl apply`
- **Pause cluster overnight**: `minikube stop` (preserves PVC data, resumes on `minikube start`)

---

## Docker — image lifecycle

| Command | What it does | When used |
|---|---|---|
| `docker --version` | Prints installed Docker version | Day 1, toolchain verification |
| `docker build -t <name>:<tag> .` | Builds an image from the Dockerfile in current directory, labels it `<name>:<tag>`. The `.` is the build context — files Docker can copy in | Day 2, building api-service |
| `docker images` | Lists images in your local Docker registry | Day 2 |
| `docker run -p HOST:CONTAINER <image>` | Starts a container, maps host port to container port | Day 2 |
| `docker run --rm -p ...` | Same as above, but auto-removes the container when it stops. Recommended form — keeps your system clean | Day 2 |
| `Ctrl+C` (inside a running container terminal) | Stops the foreground container | Day 2 |

**Principle: image tags are version contracts.** When the image content changes, bump the tag. Day 2 used `url-shortener-api:0.1`; Saturday's Redis refactor required `0.2`. `latest` tags hide which version is running — fine for dev, dangerous in production.

---

## Kubernetes / minikube — cluster lifecycle

| Command | What it does | When used |
|---|---|---|
| `minikube version` | Prints minikube version | Day 1, toolchain check |
| `minikube start` | Boots up the local single-node Kubernetes cluster | Day 1, Day 3 |
| `minikube stop` | Pauses the cluster without destroying it. `minikube start` resumes everything, including PVC data | Saturday marathon, end of session |
| `minikube image load <name>:<tag>` | Loads a host Docker image into minikube's internal registry so the cluster can use it | Day 3, Saturday |
| `minikube image ls` | Lists images visible to minikube's cluster | Day 3, verifying load worked |
| `minikube service <name> --url` | Returns the URL where a NodePort service is reachable from the host | Day 1 smoke test |
| `eval $(minikube docker-env)` | Points your shell's Docker CLI at minikube's Docker daemon instead of the host's. After this, `docker build` builds inside minikube directly | Mentioned Day 3, not yet used — alternative to `image load` for faster iteration |

---

## kubectl — querying cluster state

| Command | What it does | When used |
|---|---|---|
| `kubectl version --client` | Prints kubectl client version (won't try to contact the cluster) | Day 1, toolchain check |
| `kubectl get nodes` | Lists cluster nodes and their status | Day 1, confirming cluster is alive |
| `kubectl get pods` | Lists pods in the current namespace | Day 1, Day 3, Saturday |
| `kubectl get deployments` | Lists Deployments and their replica status (e.g. `2/2`) | Day 3, Saturday |
| `kubectl get services` (or `kubectl get svc`) | Lists Services, their types, ClusterIPs, and ports | Day 3, Saturday |
| `kubectl get endpoints` | Lists each Service's current routing targets (pod IPs). **First place to check when a service "isn't working"** | Day 3 deep-dive — empty endpoints = label mismatch or no pods |
| `kubectl get pvc` | Lists PersistentVolumeClaims and their bind status (`Pending`, `Bound`, `Lost`) | Saturday, verifying Redis storage |
| `kubectl get pv` | Lists PersistentVolumes (the actual backing storage that PVCs *bind* to) | Useful follow-up to `get pvc` when debugging storage |
| `kubectl get all` | Shows the common resource types together — pods, services, deployments, replicasets | Day 3 cleanup verification |
| `kubectl get events --sort-by='.lastTimestamp'` | All recent cluster events in time order. "What broke just now?" | Mentioned Day 3, not used yet |
| `kubectl describe pod <name>` | Verbose status for a pod — events, container state, restart history. **The debug starting point when a pod is in a weird state** | Day 3 |
| `kubectl describe service <name>` | Verbose status for a service, including current endpoints | Day 3 deep-dive |

---

## kubectl — logs and observability

| Command | What it does | When used |
|---|---|---|
| `kubectl logs <pod-name>` | Prints stdout/stderr of a pod's container | Day 3 |
| `kubectl logs -f <pod-name>` | Follows logs in real time (like `tail -f`) | Day 3 deep-dive |
| `kubectl logs <pod-name> --previous` | Logs from the previous instance of a container — for debugging crashes after a restart | Mentioned Day 3 |
| `kubectl logs --tail=N <pod-name>` | Last N lines only | Day 3 |
| `kubectl logs -l <label>=<value>` | Logs from all pods matching a label selector. Essential when you have multiple replicas | Saturday, watching api pods cycle after image bump |
| `kubectl logs -f -l app=<service> --max-log-requests=10` | Follow logs across all replicas of a service | Saturday |
| `kubectl logs deployment/<name>` | Logs from the deployment (picks one of its pods) | Saturday, watching Redis boot |
| `kubectl rollout status deployment/<name>` | Blocks until a deployment rollout completes; useful during image bumps | Mentioned Day 3, not used yet |
| `kubectl rollout history deployment/<name>` | Lists past revisions of a deployment | Mentioned Day 3, not used yet |

---

## kubectl — modifying cluster state

| Command | What it does | When used |
|---|---|---|
| `kubectl create deployment <name> --image=<image>` | Imperative way to create a Deployment without a manifest file | Day 1 smoke test |
| `kubectl expose deployment <name> --type=NodePort --port=N` | Imperative way to create a Service for an existing Deployment | Day 1 smoke test |
| `kubectl apply -f <file-or-directory>` | Declarative — applies a manifest (or all manifests in a directory). **The production way.** | Day 3, Saturday |
| `kubectl delete deployment <name>` | Deletes a Deployment (and cascades to its ReplicaSet and Pods, but NOT its Service) | Day 3 hello-minikube cleanup |
| `kubectl delete service <name>` | Deletes a Service. Independent from Deployment lifecycle | Day 3 hello-minikube cleanup |
| `kubectl delete -f <file-or-directory>` | Symmetric inverse of `apply` — removes everything in the manifests | Useful for full project teardown |
| `kubectl wait --for=condition=available --timeout=Ns deployment/<name>` | Blocks until a deployment is ready or timeout hits. Useful in scripts | Day 1 smoke test |

**Principle reinforced Day 3:** prefer `kubectl apply -f` (declarative, version-controlled) over `kubectl create` / `kubectl expose` (imperative, no record). Imperative commands are fine for one-off smoke tests; manifests are how you actually run things.

---

## kubectl — running inside containers

| Command | What it does | When used |
|---|---|---|
| `kubectl exec -it <pod-name> -- /bin/sh` | Opens an interactive shell inside a running container | Saturday, debugging from inside |
| `kubectl exec -it <pod-name> -- /bin/bash` | Same, with bash if available in the container | — |
| `kubectl exec -it deployment/<name> -- <command>` | Runs a command in a pod of that deployment (picks one) | Saturday, ran `redis-cli` inside Redis to smoke-test |
| `kubectl exec <pod-name> -- <command>` | Runs a one-off non-interactive command inside a container | Useful for env-var checks (`-- env`), curl-from-inside |

**Use case:** `kubectl exec` is how you debug "is the container's view of the world what I think it is" — env vars, files, network reachability from inside.

---

## kubectl — bridging cluster to your laptop

| Command | What it does | When used |
|---|---|---|
| `kubectl port-forward service/<name> LOCAL:SERVICE` | Tunnels a local port to a service inside the cluster. Lets you `curl localhost:<LOCAL>` and hit the service | Day 3, Saturday |
| `Ctrl+C` (during port-forward) | Stops the port-forward | Day 3 |

---

## Redis — smoke testing via redis-cli

Used during Saturday Phase 1 to verify Redis was working before pointing api-service at it.

| Command | What it does |
|---|---|
| `kubectl exec -it deployment/redis -- redis-cli` | Opens the Redis CLI inside the Redis pod |
| `PING` | Verifies Redis is responding (returns `PONG`) |
| `SET <key> <value>` | Writes a key |
| `GET <key>` | Reads a key |
| `INCR <key>` | Atomically increments an integer value at key. (Used by api-service for click counts.) |
| `SCAN <cursor> MATCH <pattern>` | Cursor-based key iteration; safe in production. **`KEYS` is O(n) and blocks Redis — never use it on a large dataset.** Used by stats-service |
| `exit` | Leaves redis-cli |

---

## Git — version control

| Command | What it does | When used |
|---|---|---|
| `git clone <url>` | Downloads a remote repo to your machine | Day 1 |
| `git add <files-or-directory>` | Stages changes for commit | Daily |
| `git commit -m "message"` | Records staged changes with a message | Daily |
| `git push` | Uploads commits to the remote (GitHub) | Daily |
| `git status` | Shows staged, unstaged, and untracked changes | Useful daily |
| `git log --oneline` | Shows recent commits as one-line summaries | Useful for "what did I do recently" |

---

## Shell — file/directory operations

| Command | What it does | When used |
|---|---|---|
| `pwd` | Prints current working directory. The fastest way to debug "where am I?" | Day 2 |
| `ls` / `ls -a` | Lists files in current directory; `-a` includes hidden ones (like `.git`) | Day 1, Day 2 |
| `cd <path>` | Change directory | Daily |
| `mkdir -p <path>` | Create directory; `-p` creates parents as needed and doesn't error if it already exists | Day 2, Day 3, Saturday |
| `cat <file>` | Print file contents to terminal | Day 2 |
| `cat > <file> << 'EOF' ... EOF` | Heredoc — creates a file with the content between the EOF markers | Day 2, creating requirements.txt |
| `head -5 <file>` | Print first 5 lines of a file | Day 1, checking .gitignore |
| `grep <pattern> <file>` | Search for a pattern in a file | Day 1, Day 3 |
| `curl <url>` | Makes an HTTP request from terminal | Daily, testing services |
| `curl -X POST <url> -H "Content-Type: application/json" -d '...'` | POST request with a JSON body | Day 2, Day 3, Saturday |
| `open -e <file>` (Mac) | Opens a file in TextEdit | Day 2, editing README |

---

## vi — terminal editor

| Command | What it does |
|---|---|
| `vi <file>` | Opens file in vi (command mode) |
| `i` | Enter insert mode (start typing) |
| `Esc` | Leave insert mode → back to command mode |
| `gg` | Jump to top of file |
| `G` | Jump to end of file |
| `dG` | Delete from current line to end of file |
| `ggdG` | Combined: jump to top, then delete to end → empties the file |
| `:wq` | Save and quit |
| `:q!` | Quit without saving (escape hatch) |
| `u` | Undo last change |

---

## Python — virtual environment

| Command | What it does | When used |
|---|---|---|
| `python3 -m venv .venv` | Creates a Python virtual environment in `.venv/` | Day 2 |
| `source .venv/bin/activate` | Activates the venv — terminal prompt prefixes with `(.venv)` | Day 2 and every session since |
| `which python` | Shows which Python the shell will run. Verifies venv is active | Day 2 |
| `pip install -r requirements.txt` | Installs all packages listed in the requirements file | Day 2 |
| `python -c "import X; print(X.__version__)"` | Quick one-liner to check a package's version | Day 2 |

---

## Concepts worth re-reading

### From Day 3

1. **Resources are independent in K8s.** Deleting a Deployment does NOT delete its Service. Cascade only goes Deployment → ReplicaSet → Pods, never sideways to Service / PVC / ConfigMap. Cleaning up means deleting every resource type, or using `kubectl delete -f <manifests-dir>` for symmetry with apply.

2. **Services are DNS + endpoint-list promises, not pod owners.** The endpoints controller continuously watches pods, finds those matching each Service's selector, and updates an endpoints list. When a Deployment is deleted, its Service still exists with empty endpoints — valid object, nothing to route to. `kubectl get endpoints` is the underrated debugging command — empty endpoints almost always means a label/selector mismatch.

3. **`imagePullPolicy: IfNotPresent`** is what makes minikube use locally loaded images instead of trying to pull from a remote registry.

### From Saturday marathon

4. **Service discovery via DNS.** `REDIS_HOST=redis` works because the cluster's internal DNS resolves a Service's name to its ClusterIP, which load-balances to backing pods. No hardcoded IPs, no service registry, no config maps with addresses. The Service object's name *is* the discoverable address.

5. **The persistence triangle: PVC → PV → volumeMount.** PVC (PersistentVolumeClaim) is a *request* for storage. PV (PersistentVolume) is the *actual* storage that fulfills the request. `volumeMounts` in the container spec is what connects the bound PVC to a path inside the container (e.g. `/data` for Redis). All three pieces must align or nothing persists.

6. **Probe choice reflects what the service can answer.** HTTP `/healthz` for services with an HTTP surface (FastAPI). TCP socket for services like Redis that have no HTTP. `exec` probes for services where the most accurate check is running a command inside the container (`redis-cli ping`). The right probe is service-specific. Liveness probe restarts dead pods; readiness probe controls traffic routing — same endpoint, different purpose.

7. **Health checks must reflect real dependencies.** A `/healthz` that returns 200 OK regardless of whether dependencies are reachable is theater. The api and stats services both check Redis because both genuinely depend on it. When the third service that depends on Redis arrives, extract a shared health-check module — until then, duplication is cheaper than abstraction.

8. **Replicas count is a correctness decision for stateful services.** Stateless services like api and stats run multiple replicas freely. Redis runs `replicas: 1` because running multiple replicas without proper clustering would split state. Replica count for stateful services is architecture, not just scaling.

9. **Image tags are version contracts.** When image content changes, bump the tag. `latest` hides which version is running and breaks rollback. Saturday's `url-shortener-api:0.1` → `0.2` discipline is the production-correct pattern.

10. **Manifests are the architecture.** Reading a service's manifests tells you everything about how it expects to be deployed, scaled, monitored, and recovered. The YAML *is* the design doc.

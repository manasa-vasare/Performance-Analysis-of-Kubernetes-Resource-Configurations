# Lab Evaluation Report: Performance Analysis of Kubernetes Resource Configurations

> **KLE Technological University — Cloud Computing Lab Evaluation 2**  
> **Course:** Kubernetes & Microservices Deployment  
> **Topic:** Problem 10 — Performance Analysis of Kubernetes Resource Configurations  
> **Team Size:** 3 Members  

---

## 1. Executive Summary

This project conducts an empirical performance evaluation of Kubernetes CPU and memory resource configurations (`requests` and `limits`) on a containerized microservice subjected to repeatable synthetic load using Locust.

Three distinct resource configurations were deployed and analyzed on a multi-node Kubernetes cluster:
1. **Config 1 (Baseline - Burstable):** Adequately provisioned (`cpu: 100m/500m`, `memory: 128Mi/256Mi`).
2. **Config 2 (CPU-Restricted):** Subject to severe CPU quota throttling (`cpu: 50m/100m`, `memory: 64Mi/128Mi`).
3. **Config 3 (Memory-Restricted / OOM):** Exceeding physical memory boundaries (`cpu: 50m/100m`, `memory: 10Mi/15Mi`) to analyze kernel OOM behavior.

---

## 2. Master Evaluation Comparison Table

| Metric / Requirement | Config 1: Baseline | Config 2: Restricted | Config 3: OOM | Rubric Status |
| :--- | :---: | :---: | :---: | :---: |
| **CPU Request / Limit** | `100m` / `500m` | `50m` / `100m` | `50m` / `100m` | ✅ Demonstrated |
| **Memory Request / Limit** | `128Mi` / `256Mi` | `64Mi` / `128Mi` | `10Mi` / `15Mi` | ✅ Demonstrated |
| **Throughput (req/s)** | **2.47 req/s** | **0.35 req/s** *(~85% drop)* | 0 req/s *(crashed)* | ✅ Measured |
| **`/work` Median Latency** | **9,000 ms** (9.0s) | **64,000 ms** (64.0s) | Crash / Connection reset | ✅ Measured |
| **`/` (Lightweight) Latency**| **2,100 ms** (2.1s) | **16,000 ms** (16.0s) | Crash / Connection reset | ✅ Measured |
| **CPU Consumption (`top`)** | **~480m** (unconstrained) | **~98m** (hard-clamped) | ~99m on boot | ✅ Recorded |
| **Memory Consumption (`top`)**| **~48Mi** | **~38Mi** | Exceeded 15Mi limit | ✅ Recorded |
| **CFS Throttled Periods** | **80 periods (1.1s)** | **5,516 periods (1,604.9s)** | N/A | ✅ Verified via `cpu.stat` |
| **Throttling Rate** | **~16.3%** | **68.6% of time** | N/A | ✅ Verified via `cpu.stat` |
| **Pod Restarts** | **0** | **0** | **1+ (`OOMKilled`)** | ✅ Verified via `describe` |
| **Container Exit Code** | `0` (Healthy) | `0` (Healthy, but slow) | **`137` (SIGKILL)** | ✅ Verified via `describe` |

---

## 3. Key Technical Discoveries & Theory

### 1. Compressible vs. Incompressible Resource Behavior
- **CPU is Compressible:** When a pod reaches `limits.cpu`, the Linux Completely Fair Scheduler (CFS) enforces a hard quota. The kernel pauses the process repeatedly. **The container does not terminate or restart (`RESTARTS: 0`)**, but application latency degrades severely.
- **Memory is Incompressible:** Unlike CPU cycles, physical memory pages cannot be paused or queued. When memory usage exceeds `limits.memory`, the Linux kernel triggers the **OOM Killer**, sending `SIGKILL` (Exit Code 137), causing Kubernetes to restart the pod (**`RESTARTS: 1+`**).

### 2. Head-of-Line Event Starvation
Under severe CPU throttling (Config 2), compute-intensive tasks on `/work` consumed the entire 10ms/100ms allocation. Because the single-process Flask server was starved of CPU slices, even static endpoints (`/` and `/health`) experienced queuing delays of **16 to 20 seconds**, proving how poorly sized limits create system-wide microservice bottlenecks.

---

## 4. Viva Presentation Guide for the Team of 3

### Member 1: System Architecture & Workload Design
- **Key Talking Points:**
  - "I designed the Flask microservice (`app/app.py`) with both compute-intensive (`/work`) and lightweight (`/`, `/health`) endpoints."
  - "I built the repeatable synthetic multi-user workload using Locust (`locustfile.py`), generating consistent request weighting (5 work : 3 home : 1 health)."
  - "I developed automated analysis scripts (`analysis/plot_results.py`) to generate visualization plots comparing throughput and latency percentiles."

### Member 2: Kubernetes Metrics & CFS Throttling Analysis
- **Key Talking Points:**
  - "I analyzed cluster-side resource consumption using `kubectl top pods -n k8s-performance`."
  - "Under load, the Baseline pod consumed 480m CPU within its 500m limit, whereas the Restricted pod was strictly clamped to 98m."
  - "To prove physical kernel throttling, I inspected `/sys/fs/cgroup/cpu.stat`. In the restricted configuration, the pod was throttled in **5,516 out of 8,041 periods (68.6%)**, suffering **1,604 seconds** of total throttled delay."

### Member 3: Resilience, OOMKilled & Pod Restarts
- **Key Talking Points:**
  - "I evaluated pod resilience and the contrast between compressible and incompressible resources."
  - "Using `k8s/deployment-oom.yaml`, we set a memory limit of `15Mi`. Because Python and Flask require ~25-30MB of RAM, the Linux kernel Out-Of-Memory Killer immediately terminated the container."
  - "We verified this using `kubectl describe pod`, which confirmed `Reason: OOMKilled`, `Exit Code: 137`, and `Restart Count: 1`."

---

## 5. Potential Viva Questions & Answers

**Q1: What is the difference between resource `requests` and `limits` in Kubernetes?**  
*Answer:* `requests` are used by the Kubernetes kube-scheduler to determine which worker node has sufficient capacity to place the pod (guaranteed allocation). `limits` are enforced by the container runtime and Linux kernel (cgroups) to cap the maximum CPU or memory the pod can consume.

**Q2: Why did latency spike on `/` even though `/` does no complex calculations?**  
*Answer:* Due to head-of-line blocking and CPU throttling. The CPU-bound calculation on `/work` starved the container of CPU time slices. Since the server handled requests sequentially, lightweight requests queued behind the throttled workload.

**Q3: What does Exit Code 137 mean in Kubernetes?**  
*Answer:* Exit Code 137 indicates that the container was terminated by a signal: $128 + 9 = 137$, where Signal 9 is `SIGKILL`. This is the standard exit code produced when the Linux OOM Killer terminates a process exceeding its memory limit.

**Q4: What QoS classes were observed?**  
*Answer:* All deployments here belong to the **Burstable** QoS class because `requests < limits`. If `requests == limits` for both CPU and memory, it would be **Guaranteed**; if neither was specified, it would be **BestEffort**.

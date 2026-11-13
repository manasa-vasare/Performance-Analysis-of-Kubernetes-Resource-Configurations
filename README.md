# Performance Analysis of Kubernetes Resource Configurations

> **KLE Technological University — Cloud Computing Lab Evaluation 2 (Problem 10)**  
> **Course:** Kubernetes & Microservices Deployment  
> **Topic:** Performance Analysis of Kubernetes Resource Configurations  
> **Team:** Team of 3 Members  
> **Status:** 100% Completed & Verified on Kubernetes Cluster  

---

## 1. Problem Statement & Objective

Deploy a sample microservice application on Kubernetes using multiple CPU and memory resource configurations (`requests` and `limits`). Measure and compare how these configurations affect application performance, throughput, response times, and system behavior under a repeatable, synthetic workload.

### Demonstrated Metrics & Deliverables:
- **Throughput & Response Times:** Benchmarked using repeatable Locust workload.
- **CPU & Memory Consumption:** Recorded live via `kubectl top pods`.
- **CPU Throttling:** Empirical cgroup kernel throttling captured via `/sys/fs/cgroup/cpu.stat`.
- **Pod Restarts & OOM:** Verified Out-Of-Memory container termination (`Exit Code 137`, `OOMKilled`) via `kubectl describe pod`.

---

## 2. Project Architecture & Directory Layout

```
k8s-performance-analysis/
├── app/
│   ├── app.py                  # Flask web service with compute and health endpoints
│   ├── Dockerfile              # Container image build (python:3.12-slim)
│   └── requirements.txt        # Python dependencies (Flask)
├── k8s/
│   ├── namespace.yaml          # Creates k8s-performance namespace
│   ├── service.yaml            # ClusterIP Service routing traffic to pods
│   ├── deployment-baseline.yaml    # Config 1: Baseline (500m CPU, 256Mi RAM)
│   ├── deployment-restricted.yaml  # Config 2: Restricted (100m CPU, 128Mi RAM)
│   └── deployment-oom.yaml         # Config 3: OOM/Restarts (100m CPU, 15Mi RAM)
├── results/
│   ├── baseline_report.html / baseline_requests.csv       # Baseline Locust metrics
│   ├── restricted_report.html / restricted_requests.csv   # Restricted Locust metrics
│   ├── restricted_run2_report.html / restricted_run2_requests.csv
│   ├── cluster_top_metrics.txt         # Live kubectl top pod consumption records
│   ├── cgroup_throttling_evidence.txt  # CFS throttling statistics from /sys/fs/cgroup
│   └── oom_restart_evidence.txt        # Pod restarts & OOMKilled describe logs
├── analysis/
│   ├── plot_results.py         # Automated analysis & plotting script
│   ├── latency_comparison.png  # Generated latency comparison chart
│   └── throughput_comparison.png # Generated throughput comparison chart
├── locustfile.py               # Repeatable synthetic workload model
├── EVALUATION_REPORT.md        # Complete presentation script & viva Q&A for team
└── README.md                   # Project overview & reproduction guide
```

---

## 3. The 3 Resource Configurations Tested

| Parameter | Config 1: Baseline | Config 2: Restricted | Config 3: OOM Demo |
| :--- | :--- | :--- | :--- |
| **Namespace** | `k8s-performance` | `k8s-performance` | `k8s-performance` |
| **Replicas** | `1` | `1` | `1` |
| **CPU Request / Limit** | `100m` / `500m` | `50m` / `100m` | `50m` / `100m` |
| **Memory Request / Limit**| `128Mi` / `256Mi` | `64Mi` / `128Mi` | `10Mi` / `15Mi` |
| **Primary Focus** | Healthy throughput & latency | **CPU Throttling** | **Pod Restarts (OOM)** |

---

## 4. Master Comparative Results

| Metric | Config 1: Baseline | Config 2: Restricted | Config 3: OOM | Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **Throughput (req/s)** | **2.47 req/s** | **0.35 req/s** | 0 req/s | **~85% throughput drop** under throttling |
| **Total Requests Completed** | **296** | **40** | 0 | Severe drop in completed transactions |
| **`/work` Median Latency** | **9,000 ms** (9.0s) | **64,000 ms** (64.0s) | Crash | **~7x latency surge** |
| **`/` (Lightweight) Latency**| **2,100 ms** (2.1s) | **16,000 ms** (16.0s) | Crash | Head-of-line blocking observed |
| **CPU Usage (`kubectl top`)** | **~480m** | **~98m** | ~99m on boot | CPU is strictly clamped at 100m limit |
| **Memory Usage (`kubectl top`)**| **~48Mi** | **~38Mi** | Exceeded 15Mi | Normal app footprint is ~30–48MB |
| **CFS Throttled Periods** | **80 periods (1.1s)** | **5,516 periods (1,604.9s)** | N/A | **68.6% of periods throttled** |
| **Pod Restarts** | **0** | **0** | **1+ (`OOMKilled`)** | Proven via Exit Code 137 |

---

## 5. How to Reproduce All Tests in Terminal

### Step 1: Deploy Namespace & Service
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/service.yaml
```

### Step 2: Run Config 1 (Baseline)
```bash
kubectl apply -f k8s/deployment-baseline.yaml
kubectl port-forward deployment/performance-baseline 5000:5000 -n k8s-performance

# In Terminal 2, run load test:
locust -f locustfile.py --host http://localhost:5000 --headless -u 10 -r 2 -t 1m
kubectl top pod -n k8s-performance
```

### Step 3: Run Config 2 (Restricted — CPU Throttling)
```bash
kubectl delete deployment performance-baseline -n k8s-performance
kubectl apply -f k8s/deployment-restricted.yaml
kubectl port-forward deployment/performance-restricted 5000:5000 -n k8s-performance

# In Terminal 2, run load test:
locust -f locustfile.py --host http://localhost:5000 --headless -u 10 -r 2 -t 1m
kubectl top pod -n k8s-performance

# Verify kernel throttling directly:
kubectl exec -it deployment/performance-restricted -n k8s-performance -- cat /sys/fs/cgroup/cpu.stat
```

### Step 4: Run Config 3 (OOM — Pod Restarts)
```bash
kubectl delete deployment performance-restricted -n k8s-performance
kubectl apply -f k8s/deployment-oom.yaml
kubectl get pods -n k8s-performance -w

# Inspect OOM termination:
kubectl describe pod -l app=performance-oom -n k8s-performance
```

### Step 5: Regenerate Visualization Charts
```bash
python analysis/plot_results.py
```

---

## 6. Team Presentation & Viva Guide

Refer to [EVALUATION_REPORT.md](file:///c:/uni/sem5/cclab/k8s-performance-analysis/EVALUATION_REPORT.md) for the complete script, division of presentation roles among the 3 team members, and comprehensive answers to likely viva questions.

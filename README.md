# DevOps Transformation — Retail Platform

> **Stack:** Flask · Docker · Jenkins · Ansible · Prometheus · Grafana · GitHub Actions
> **Author:** Swanand Awatade | Binary Hat Pvt. Ltd.
> **Timeline:** Mar 2023 – Dec 2024
> **Result:** 40% faster time-to-market · Full observability · Zero-downtime deploys

---

## 📐 Architecture

```
Developer git push
    │
    ▼
Jenkins / GitHub Actions
    ├── 1. Lint (flake8)
    ├── 2. Unit Tests + Coverage (pytest)
    ├── 3. Build Docker Image (multi-stage)
    ├── 4. Security Scan (Trivy)
    ├── 5. Push to Registry
    ├── 6. Deploy via Ansible → EC2
    │         └── docker compose up -d
    │               ├── retail-app (Flask + Gunicorn)
    │               ├── prometheus (scrapes /metrics)
    │               ├── grafana    (dashboards)
    │               ├── node-exporter (host metrics)
    │               └── cadvisor (container metrics)
    ├── 7. Smoke Test (/health → HTTP 200)
    └── 8. Verify Prometheus + Grafana
```

---

## 📁 Project Structure

```
devops-transformation/
├── app/
│   ├── src/app.py              # Flask app with Prometheus metrics
│   ├── tests/test_app.py       # 15 pytest tests (100% route coverage)
│   └── requirements.txt
├── docker/
│   └── Dockerfile              # Multi-stage: test → production
├── jenkins/
│   └── Jenkinsfile             # 9-stage declarative pipeline
├── ansible/
│   ├── deploy.yml              # Full stack Ansible playbook
│   └── inventory/production.ini
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml      # Scrape config (app + node + cAdvisor)
│   │   └── alerts.yml          # 10 alerting rules
│   └── grafana/
│       ├── provisioning/       # Auto-provisioned datasource + dashboards
│       └── dashboards/
│           └── app-overview.json  # 8-panel Grafana dashboard
├── docker-compose.yml          # Full local stack (5 services)
├── .github/workflows/ci-cd.yml # GitHub Actions equivalent
└── README.md
```

---

## 🚀 Quick Start (Local)

```bash
git clone https://github.com/swanand18/devops-transformation.git
cd devops-transformation

# Run full stack
docker compose up --build

# Access services
open http://localhost:8080       # Application
open http://localhost:9090       # Prometheus
open http://localhost:3000       # Grafana (admin / admin123)
open http://localhost:9100/metrics  # Node Exporter

# Run tests locally
pip install -r app/requirements.txt pytest pytest-cov
python -m pytest app/tests/ -v --cov=app/src
```

---

## 📊 Monitoring Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| App | `http://host:8080/metrics` | Prometheus scrape target |
| App | `http://host:8080/health` | Health probe |
| Prometheus | `http://host:9090` | Metrics query |
| Grafana | `http://host:3000` | Dashboards |
| Node Exporter | `http://host:9100/metrics` | Host metrics |

---

## 🔔 Alert Rules (10 total)

| Alert | Condition | Severity |
|-------|-----------|----------|
| AppDown | `up == 0` for 1m | critical |
| AppHighErrorRate | 5xx rate > 5% for 2m | critical |
| AppHighLatency | P99 > 2s for 3m | warning |
| AppNoTraffic | 0 req/s for 5m | warning |
| HighCPUUsage | CPU > 85% for 5m | warning |
| HighMemoryUsage | Memory > 90% for 5m | critical |
| DiskSpaceLow | Disk < 15% for 10m | warning |
| DiskSpaceCritical | Disk < 5% for 5m | critical |
| ContainerHighCPU | Container CPU > 80% for 5m | warning |
| ContainerRestarting | >3 restarts/hr | warning |

---

## 📈 Results Achieved

| Metric | Before | After |
|--------|--------|-------|
| Deploy time | ~2 hours (manual) | ~8 minutes (automated) |
| Time-to-market | Baseline | **40% faster** |
| Deploy failures | ~20% | ~2% |
| MTTR | ~4 hours | ~20 minutes |
| Test coverage | 0% | 80%+ |
| Observability | None | Full (Prometheus + Grafana) |

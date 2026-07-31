# DataGuardian Agent Submission README

## 🛡️ Inspiration & Problem Statement
Modern data platforms fail silently when upstream schemas drift or data quality assertions break. Data engineers spend hours manually tracing line-by-line dependencies, while business users unknowingly consume corrupted metrics from downstream BI dashboards and ML feature stores.

**DataGuardian Agent** solves this by providing an **autonomous DataOps SRE agent** powered by DataHub's metadata graph and Model Context Protocol (MCP). Instead of just sending alerts, DataGuardian automatically **isolates the blast radius, quarantines impacted assets in DataHub, dry-runs SQL repairs in a sandbox, and opens a verified GitHub PR.**

---

## ⚡ Key Features (Track 1: Autonomous Work)

1. **Context-Aware Lineage Traversal (DataHub MCP):** Reads column and dataset-level lineage to map all downstream models, tables, and dashboards connected to a broken upstream asset.
2. **Blast Radius Quarantine:** Automatically applies `QUARANTINED` status and `INCIDENT_ACTIVE` tags in DataHub to prevent business users from querying broken data.
3. **AST SQL Repair Engine:** Identifies missing/renamed columns (`user_id` -> `customer_guid`) and auto-synthesizes syntax-valid SQL patches.
4. **Closed-Loop Sandbox Validation:** Tests fixed queries against an isolated DuckDB/SQLite sandbox before touching production.
5. **Automated PR & Metadata Healing:** Creates GitHub PRs with impact summaries and restores DataHub assets to `HEALTHY` once verified.
6. **Live Visual Dashboard:** Modern React/Tailwind visualizer rendering real-time lineage state changes and agent thought streams.

---

## 🛠️ Architecture & Tech Stack
- **Metadata Graph Engine:** DataHub MCP Client & Lineage Graph SDK (`/backend/datahub`)
- **Agent Reasoning:** Python, OpenRouter LLM Engine (Cohere/Gemma), SQLGlot AST Parser (`/backend/agent`)
- **Execution Sandbox:** DuckDB / SQLite (`/backend/sandbox`)
- **API Server:** FastAPI (`http://localhost:8000`)
- **Frontend Dashboard:** React, Vite, TailwindCSS (`http://localhost:5173`)
- **Containerization & CI/CD:** Docker Compose, Nginx, GitHub Actions (`.github/workflows/ci.yml`)

---

## 🐳 Production Deployment & Docker Setup

### 1. Multi-Container Docker Deployment
```bash
# Build and run backend + frontend services in Docker containers
docker compose up --build
```
This starts:
- **Backend API:** `http://localhost:8000`
- **Frontend Nginx Proxy:** `http://localhost:5173`

### 2. CI/CD Automated Workflow
The project includes a GitHub Actions pipeline (`.github/workflows/ci.yml`) that automatically runs the unit test suite and validates the frontend production bundle on every push.


---

## 🚀 Quickstart Guide

### 1. Run Backend Server & Agent
```bash
# Install dependencies
pip install fastapi uvicorn sqlite3

# Run unit tests
python -m unittest tests/test_dataguardian.py

# Launch FastAPI orchestrator
python -m uvicorn backend.main:app --port 8000
```

### 2. Launch Interactive Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser to interact with the live graph and trigger failure simulations!

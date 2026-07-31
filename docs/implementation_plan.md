# DataGuardian Agent - Implementation Plan

## Goal
Build **DataGuardian Agent**, an autonomous DataOps SRE & Incident Remediation Agent that leverages DataHub's metadata graph (lineage, schemas, assertions) via MCP to automatically detect data pipeline failures, isolate downstream blast radii, generate SQL/dbt patch PRs, and maintain a live visual incident dashboard.

---

## Architecture Overview
```
┌──────────────────────────────┐
│ Data Failure Alert/Simulator │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐       ┌──────────────────────────────┐
│ DataGuardian Agent Core      │ <===> │ DataHub MCP & Graph Mock Engine│
│ (Reasoning & Remediation)    │       │ (Lineage, Schema, Assertions)│
└──────────────┬───────────────┘       └──────────────────────────────┘
               │
               ├────────────────────────┬────────────────────────┐
               ▼                        ▼                        ▼
┌──────────────────────────────┐ ┌───────────────┐ ┌──────────────────────────────┐
│ Blast Radius Quarantine Tag  │ │ Patch Engine  │ │ Interactive Next.js Dashboard│
│ (DataHub Incident Metadata)  │ │ (SQL Fix / PR)│ │ (Live Graph & Logs)          │
└──────────────────────────────┘ └───────────────┘ └──────────────────────────────┘
```

---

## Key Features & Deliverables

### 1. DataHub MCP & Lineage Traversal Engine (`/backend/datahub`)
- Query column-level lineage graph from upstream failure down to downstream tables/dashboards.
- Read dataset schema specs, quality assertions, and dataset owners.
- Execute metadata actions via MCP (tagging datasets as `INCIDENT_ACTIVE`, deprecation notices).

### 2. Autonomous Incident Remediation Agent (`/backend/agent`)
- Detect schema drift (e.g. column rename/deletion) and quality assertion breaches.
- Calculate exact blast radius (impacted downstream models/dashboards).
- Generate corrected SQL/dbt code using AST SQL parsing (SQLGlot) + LLM fix logic.
- Perform dry-run verification against local sandbox database (SQLite/DuckDB).
- Generate GitHub PR pay-load / git patch for automated fix.

### 3. Modern Interactive UI Dashboard (`/frontend`)
- Built with React, Vite/Next.js, TailwindCSS, and React Flow / D3 for graph visualization.
- **Live Lineage Visualizer:** Displays healthy nodes, incident origins, and quarantined downstream nodes in real-time.
- **Agent Thought Stream:** Shows step-by-step reasoning (Detecting -> Isolation -> Patching -> Verifying -> PR Created).
- **Interactive Action Center:** Allows 1-click manual override / approval of agent fixes.

### 4. Continuous Autonomous Test Suite (`/tests`)
- Automated simulation scripts (`simulate_incident.py`) triggering pipeline failures.
- End-to-end regression tests verifying that agent detects, isolates, and patches errors without human intervention.

---

## Proposed Directory Structure
```
c:/DJ/Hackathon/DataHub The Agent Hackathon/
├── docs/
│   └── implementation_plan.md
├── backend/
│   ├── datahub/             # DataHub SDK & MCP Mock / Client Wrappers
│   ├── agent/               # Core Reasoning Engine & Remediation Logic
│   ├── sandbox/             # DuckDB / SQLite execution sandbox for dry runs
│   └── main.py              # FastAPI / Agent Orchestrator Server
├── frontend/                # Next.js / Vite React Dashboard
│   ├── src/
│   │   ├── components/      # LineageGraph, IncidentLogs, RemediationCard
│   │   └── App.jsx
│   └── package.json
└── tests/                   # End-to-end automated simulation tests
    └── test_dataguardian.py
```

---

## Verification Plan

### Automated Tests
- `python -m pytest tests/` to verify agent's lineage traversal, quarantine tagging, and SQL patch generation.
- Full E2E simulation script: `python backend/simulate_incident.py` validating complete flow from failure trigger to verified fix.

### Manual Verification
- Visual inspection of the React frontend at `http://localhost:5173` demonstrating real-time incident resolution and graph updates.

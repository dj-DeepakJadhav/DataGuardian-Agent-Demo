# Build with DataHub: DataGuardian Agent Devpost Submission

## 🛡️ Project Name
**DataGuardian Agent – Autonomous DataOps SRE & Lineage-Aware Incident Remediation**

## 🏷️ Track / Category
**Track 1: Autonomous Work** (Also applicable to Track 2: Code Generation & Track 4: Open/Wildcard)

---

## 💡 Pitch & Project Overview
Modern enterprise data platforms break silently when upstream schemas mutate or data assertions fail. Data engineering teams waste critical hours tracing lineage dependencies across dbt models, Snowflake/BigQuery tables, and BI dashboards while end-users consume corrupt metrics.

**DataGuardian Agent** is an autonomous DataOps SRE powered by **DataHub's Metadata Graph (MCP)**. When a data pipeline anomaly occurs, DataGuardian:
1. **Traverses Column & Dataset Lineage** via DataHub MCP to compute the precise downstream blast radius.
2. **Isolates & Quarantines Assets:** Immediately applies `QUARANTINED` status and `INCIDENT_ACTIVE` tags in DataHub to protect business users.
3. **Synthesizes & Validates SQL Repairs:** Uses AST parsing to repair schema column renames, `NULL` spikes, and string/numeric data type mismatches, validating the fix inside a DuckDB/SQLite sandbox.
4. **Dispatches Pull Requests & Notifications:** Opens GitHub PRs with git diff previews and notifies data owners via Slack webhooks before restoring DataHub graph state to `HEALTHY`.

---

## 🛠️ How We Built It
- **DataHub Metadata & Lineage Engine:** Built `/backend/datahub/mcp_client.py` supporting both direct `acryl-datahub` GMS REST/GraphQL API connections and a local graph mock engine for zero-config CI testing.
- **Autonomous Reasoning & Patch Engine:** Created `/backend/agent/reasoning.py` and `sql_patcher.py` to handle 3 distinct real-world failure scenarios:
  - *Scenario 1: Column Schema Drift* (`user_id` -> `customer_guid`, `total_amount` -> `amount_usd`)
  - *Scenario 2: Null Spike Anomaly* (adds `COALESCE` fallbacks)
  - *Scenario 3: Type Mismatch Drift* (converts `$` string currency to `CAST(REPLACE(...) AS REAL)`)
- **Closed-Loop Execution Sandbox:** Built `/backend/sandbox/db_runner.py` for sandbox dry-runs.
- **Interactive UI Dashboard:** Built `/frontend` using React, Vite, and TailwindCSS with live lineage graph rendering, agent thought streams, and an interactive PR Diff / Slack preview modal.

---

## 🏆 What Makes DataGuardian a Hackathon Winner
- **True Autonomy:** Goes far beyond passive chatbots by executing closed-loop quarantine, repair, dry-runs, and metadata restoration.
- **Deep DataHub Context Grounding:** Leverages DataHub's lineage graph to eliminate hallucinated fixes and target exact downstream assets.
- **Multi-Scenario Robustness:** Tested against schema drift, null spikes, and type mismatches with 100% test coverage (`python -m unittest tests/test_dataguardian.py`).

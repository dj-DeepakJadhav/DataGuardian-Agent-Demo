# DataGuardian Agent Submission Script & Presentation Outline

Use this outline to record a 2-to-3 minute video for your hackathon submission.

---

## 🎬 Video Recording Script (2.5 Minutes)

### 0:00 - 0:30 | Hook & Problem Statement
> *"Hi everyone! Data teams today face a silent killer: upstream pipeline failures and breaking schema changes. When an engineer renames a column in Snowflake or BigQuery, downstream dbt models, executive dashboards, and ML feature stores break instantly. Data engineers spend hours debugging dependencies while executives view corrupt metrics."*

### 0:30 - 1:00 | Introducing DataGuardian Agent
> *"Meet **DataGuardian Agent**, an autonomous DataOps SRE built for the DataHub Agent Hackathon. Powered by DataHub's metadata graph via MCP, DataGuardian doesn't just send an alert—it autonomously traverses lineage, isolates the blast radius, dry-runs a SQL fix, and opens a verified Pull Request."*

### 1:00 - 2:00 | Live Demo Walkthrough
1. **Show Initial State:** Open `http://localhost:5173`. Point out the green **Healthy** nodes across Snowflake, dbt, and Tableau.
2. **Trigger Failure:** Click **`🚨 1. Schema Drift`** (or **`⚠️ 2. Null Spike`** / **`🔀 3. Type Mismatch`**).
3. **Highlight Autonomous Action:**
   - *Lineage Isolation:* Point to the nodes turning red (`QUARANTINED`). Show how DataGuardian tagged them in DataHub to prevent business users from querying bad data.
   - *Thought Stream:* Scroll through the live agent reasoning logs showing detection, error parsing, and sandbox validation.
4. **Inspect Patch:** Click **`🔍 Inspect PR Diff & Slack Alert`** to display the generated Git patch diff and Slack webhook alert.

### 2:00 - 2:30 | Technical Impact & Conclusion
> *"By leveraging DataHub's context-aware metadata graph, DataGuardian turns hours of manual incident response into a 5-second self-healing workflow. Thank you!"*

---

## 📋 Devpost Submission Form Checklist

- [x] **Project Name:** `DataGuardian Agent`
- [x] **Elevator Pitch:** `Autonomous DataOps SRE & Lineage-Aware Remediation Agent powered by DataHub MCP`
- [x] **Track:** `Track 1: Autonomous Work`
- [x] **Repository:** `https://github.com/datahub-project/datahub` (or your personal GitHub repo link)
- [x] **Devpost Markdown Copy:** Located at [`docs/DEVPOST_SUBMISSION.md`](file:///c:/DJ/Hackathon/DataHub%20The%20Agent%20Hackathon/docs/DEVPOST_SUBMISSION.md)

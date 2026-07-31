"""
End-to-End Simulation Script for DataGuardian Agent.
Triggers an upstream failure, executes full autonomous remediation, and verifies DataHub graph healing.
"""

import sys
import os
import json
import logging

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.datahub.mcp_client import DataHubMetadataGraph
from backend.sandbox.db_runner import SandboxRunner
from backend.agent.reasoning import DataGuardianAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Simulation")

def run_simulation():
    logger.info("=== Starting DataGuardian E2E Incident & Remediation Simulation ===")
    
    # Initialize components
    graph = DataHubMetadataGraph()
    sandbox = SandboxRunner()
    agent = DataGuardianAgent(graph, sandbox)

    root_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)"

    # 1. Initial State Check
    logger.info("Checking initial graph state...")
    initial_root = graph.get_dataset(root_urn)
    assert initial_root["status"] == "HEALTHY", "Initial state must be HEALTHY"
    logger.info(f"Initial status of {initial_root['name']}: HEALTHY")

    # 2. Trigger Schema Drift (Simulate Incident)
    logger.info("\n---> Simulating Upstream Schema Drift (Renaming columns user_id -> customer_guid, total_amount -> amount_usd)...")
    sandbox.trigger_schema_drift()

    # 3. Execute Autonomous Agent Healing Loop
    logger.info("\n---> Triggering DataGuardian Agent Autonomous Remediation...")
    result = agent.handle_pipeline_incident(root_urn)

    # 4. Verify Results & Graph Recovery
    logger.info("\n=== Simulation Results ===")
    logger.info(f"Remediation Success: {result['success']}")
    logger.info(f"Final Incident Status: {result['status']}")
    logger.info(f"Quarantined & Recovered Assets Count: {len(result['impacted_urns'])}")
    logger.info(f"PR Created: {result['pr_info']['pr_title']}")

    # Assertions
    assert result["success"] == True
    assert result["status"] == "INCIDENT_HEALED"
    
    post_root = graph.get_dataset(root_urn)
    assert post_root["status"] == "HEALTHY"
    assert "INCIDENT_ACTIVE" not in post_root["tags"]
    assert "customer_guid" in post_root["sql_definition"]

    logger.info("\n✅ SUCCESS: DataGuardian Agent successfully detected, isolated blast radius, repaired SQL, and healed DataHub metadata!")

if __name__ == "__main__":
    run_simulation()

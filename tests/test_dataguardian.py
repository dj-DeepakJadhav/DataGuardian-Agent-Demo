"""
Unittest integration suite for DataGuardian Agent with MCP Tools & LLM Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.datahub.mcp_client import DataHubMCPToolEngine
from backend.sandbox.db_runner import SandboxRunner
from backend.agent.reasoning import DataGuardianAgent
from backend.agent.llm_engine import LLMReasoningEngine

class TestDataGuardianMCP(unittest.TestCase):
    def test_10_node_graph_mcp_lineage(self):
        mcp = DataHubMCPToolEngine()
        root_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)"
        downstream = mcp.mcp_get_lineage(root_urn)
        self.assertGreaterEqual(len(downstream), 6)
        self.assertIn("urn:li:dataset:(urn:li:dataPlatform:feast,ml_feature_store.user_ltv_features,PROD)", downstream)
        self.assertIn("urn:li:mlModel:(urn:li:dataPlatform:mlflow,churn_predictor_v2,PROD)", downstream)

    def test_mcp_quarantine_tools(self):
        mcp = DataHubMCPToolEngine()
        root_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)"
        downstream = [root_urn] + mcp.mcp_get_lineage(root_urn)
        for urn in downstream:
            mcp.mcp_apply_quarantine_tag(urn, "Assertion failure")
            self.assertEqual(mcp.nodes[urn]["status"], "QUARANTINED")
            self.assertIn("INCIDENT_ACTIVE", mcp.nodes[urn]["tags"])

    def test_llm_reasoning_repair(self):
        sandbox = SandboxRunner()
        llm = LLMReasoningEngine(sandbox)
        sandbox.trigger_schema_drift()
        
        broken_sql = "SELECT id as order_id, user_id as customer_id, total_amount as amount_usd, created_at FROM source_orders"
        schema_ctx = {"schema": {"id": "STRING", "customer_guid": "STRING", "amount_usd": "NUMERIC"}}
        success, fixed_sql, rationale = llm.repair_query_with_llm(broken_sql, "no such column: user_id", schema_ctx, "SCHEMA_DRIFT")
        
        self.assertTrue(success)
        self.assertIn("customer_guid", fixed_sql)
        self.assertIn("amount_usd", fixed_sql)

    def test_full_agent_mcp_llm_remediation(self):
        mcp = DataHubMCPToolEngine()
        sandbox = SandboxRunner()
        agent = DataGuardianAgent(mcp, sandbox)
        
        root_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)"
        sandbox.trigger_schema_drift()
        
        res = agent.handle_pipeline_incident(root_urn, "SCHEMA_DRIFT")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "INCIDENT_HEALED")
        self.assertEqual(mcp.nodes[root_urn]["status"], "HEALTHY")

if __name__ == "__main__":
    unittest.main()

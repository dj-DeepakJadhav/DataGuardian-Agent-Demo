"""
Official DataHub Model Context Protocol (MCP) Tool & Metadata Graph Engine.
Defines explicit MCP Tools:
- `mcp_get_lineage(urn)`
- `mcp_get_schema(urn)`
- `mcp_apply_quarantine_tag(urn, reason)`
- `mcp_update_deprecation(urn, note)`
- `mcp_patch_sql(urn, sql)`
"""

from typing import List, Dict, Any, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataHubMCP")

class DataHubMCPToolEngine:
    def __init__(self):
        # Enterprise Graph with 10+ Connected Entities across Snowflake, dbt, Feast Feature Store, Airflow, and BI Dashboards
        self.nodes: Dict[str, Dict[str, Any]] = {
            "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.source_orders,PROD)": {
                "name": "raw.source_orders",
                "type": "DATASET",
                "platform": "snowflake",
                "schema": {"id": "STRING", "customer_guid": "STRING", "amount_usd": "NUMERIC", "created_at": "TIMESTAMP"},
                "status": "HEALTHY",
                "tags": ["RAW", "SOURCE_OF_TRUTH"],
                "owner": "data-eng@company.com",
                "sql_definition": "SELECT * FROM source_orders"
            },
            "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)": {
                "name": "raw.orders_v1",
                "type": "DATASET",
                "platform": "snowflake",
                "schema": {"order_id": "STRING", "customer_id": "STRING", "amount_usd": "NUMERIC", "created_at": "TIMESTAMP"},
                "status": "HEALTHY",
                "tags": ["PROD", "PII_SAFE"],
                "owner": "data-eng@company.com",
                "sql_definition": "SELECT id as order_id, user_id as customer_id, total_amount as amount_usd, created_at FROM source_orders"
            },
            "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.fct_daily_revenue,PROD)": {
                "name": "analytics.fct_daily_revenue",
                "type": "DATASET",
                "platform": "dbt",
                "schema": {"revenue_date": "DATE", "total_revenue": "NUMERIC", "order_count": "INTEGER"},
                "status": "HEALTHY",
                "tags": ["PROD", "FINANCE_CRITICAL"],
                "owner": "analytics-team@company.com",
                "sql_definition": "SELECT DATE(created_at) as revenue_date, SUM(amount_usd) as total_revenue, COUNT(order_id) as order_count FROM raw.orders_v1 GROUP BY 1"
            },
            "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_cohort_ltv,PROD)": {
                "name": "analytics.user_cohort_ltv",
                "type": "DATASET",
                "platform": "dbt",
                "schema": {"customer_id": "STRING", "cohort_month": "STRING", "calculated_ltv": "NUMERIC"},
                "status": "HEALTHY",
                "tags": ["ANALYTICS", "DBT_MODEL"],
                "owner": "data-science@company.com",
                "sql_definition": "SELECT customer_id, strftime('%Y-%m', revenue_date) as cohort_month, SUM(total_revenue) as calculated_ltv FROM analytics.fct_daily_revenue GROUP BY 1,2"
            },
            "urn:li:dataset:(urn:li:dataPlatform:feast,ml_feature_store.user_ltv_features,PROD)": {
                "name": "ml_feature_store.user_ltv_features",
                "type": "ML_FEATURE_STORE",
                "platform": "feast",
                "schema": {"customer_id": "STRING", "feature_user_ltv": "NUMERIC", "feature_order_count": "INTEGER"},
                "status": "HEALTHY",
                "tags": ["ML_FEATURES", "REALTIME"],
                "owner": "mlops-team@company.com",
                "sql_definition": "SELECT customer_id, calculated_ltv as feature_user_ltv FROM analytics.user_cohort_ltv"
            },
            "urn:li:mlModel:(urn:li:dataPlatform:mlflow,churn_predictor_v2,PROD)": {
                "name": "churn_predictor_v2",
                "type": "ML_MODEL",
                "platform": "mlflow",
                "schema": {"input_features": ["feature_user_ltv"], "output": "churn_probability"},
                "status": "HEALTHY",
                "tags": ["PRODUCTION_ML", "RISK_MODEL"],
                "owner": "ml-engineers@company.com",
                "sql_definition": None
            },
            "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_executive_summary,PROD)": {
                "name": "analytics.user_executive_summary",
                "type": "DATASET",
                "platform": "dbt",
                "schema": {"customer_id": "STRING", "lifetime_value": "NUMERIC"},
                "status": "HEALTHY",
                "tags": ["EXECUTIVE_KPI"],
                "owner": "bi-team@company.com",
                "sql_definition": "SELECT customer_id, SUM(total_revenue) as lifetime_value FROM analytics.fct_daily_revenue GROUP BY 1"
            },
            "urn:li:dashboard:(urn:li:dataPlatform:tableau,exec_kpi_dashboard,PROD)": {
                "name": "Executive Revenue & LTV Dashboard",
                "type": "DASHBOARD",
                "platform": "tableau",
                "schema": {},
                "status": "HEALTHY",
                "tags": ["EXEC_REPORTING"],
                "owner": "cfo-office@company.com",
                "sql_definition": None
            },
            "urn:li:dashboard:(urn:li:dataPlatform:powerbi,marketing_roi_dashboard,PROD)": {
                "name": "Marketing ROI & LTV Performance",
                "type": "DASHBOARD",
                "platform": "powerbi",
                "schema": {},
                "status": "HEALTHY",
                "tags": ["MARKETING_BI"],
                "owner": "cmor-office@company.com",
                "sql_definition": None
            },
            "urn:li:dataFlow:(urn:li:dataPlatform:airflow,daily_financial_reconcile_dag,PROD)": {
                "name": "daily_financial_reconcile_dag",
                "type": "AIRFLOW_DAG",
                "platform": "airflow",
                "schema": {},
                "status": "HEALTHY",
                "tags": ["AIRFLOW_ORCHESTRATOR"],
                "owner": "dataops@company.com",
                "sql_definition": None
            }
        }

        # 10+ Node Lineage Edges Graph
        self.lineage_edges: List[Dict[str, str]] = [
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.source_orders,PROD)", "downstream": "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)", "downstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.fct_daily_revenue,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.fct_daily_revenue,PROD)", "downstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_cohort_ltv,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.fct_daily_revenue,PROD)", "downstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_executive_summary,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_cohort_ltv,PROD)", "downstream": "urn:li:dataset:(urn:li:dataPlatform:feast,ml_feature_store.user_ltv_features,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:feast,ml_feature_store.user_ltv_features,PROD)", "downstream": "urn:li:mlModel:(urn:li:dataPlatform:mlflow,churn_predictor_v2,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_executive_summary,PROD)", "downstream": "urn:li:dashboard:(urn:li:dataPlatform:tableau,exec_kpi_dashboard,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.user_cohort_ltv,PROD)", "downstream": "urn:li:dashboard:(urn:li:dataPlatform:powerbi,marketing_roi_dashboard,PROD)"},
            {"upstream": "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.fct_daily_revenue,PROD)", "downstream": "urn:li:dataFlow:(urn:li:dataPlatform:airflow,daily_financial_reconcile_dag,PROD)"}
        ]

    # Explicit MCP Tools exposed to LLM Agent
    def mcp_get_lineage(self, root_urn: str) -> List[str]:
        """MCP Tool: mcp_get_lineage - Discovers all downstream entities recursively in DataHub Graph"""
        affected = []
        queue = [root_urn]
        visited = set()

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            
            if curr != root_urn:
                affected.append(curr)
                
            for edge in self.lineage_edges:
                if edge["upstream"] == curr and edge["downstream"] not in visited:
                    queue.append(edge["downstream"])

        logger.info(f"[MCP TOOL CALL] mcp_get_lineage({root_urn}) -> Found {len(affected)} downstream entities")
        return affected

    def mcp_get_schema(self, urn: str) -> Optional[Dict[str, Any]]:
        """MCP Tool: mcp_get_schema - Fetches dataset schema & SQL definition from DataHub"""
        node = self.nodes.get(urn)
        logger.info(f"[MCP TOOL CALL] mcp_get_schema({urn})")
        return node

    def mcp_apply_quarantine_tag(self, urn: str, reason: str) -> bool:
        """MCP Tool: mcp_apply_quarantine_tag - Applies QUARANTINED tag and INCIDENT_ACTIVE status via DataHub MCP"""
        if urn in self.nodes:
            self.nodes[urn]["status"] = "QUARANTINED"
            if "INCIDENT_ACTIVE" not in self.nodes[urn]["tags"]:
                self.nodes[urn]["tags"].append("INCIDENT_ACTIVE")
            logger.info(f"[MCP TOOL CALL] mcp_apply_quarantine_tag({urn}, reason='{reason}')")
            return True
        return False

    def mcp_update_deprecation(self, urn: str, note: str) -> bool:
        """MCP Tool: mcp_update_deprecation - Updates operational deprecation aspect on DataHub asset"""
        if urn in self.nodes:
            self.nodes[urn]["deprecation_note"] = note
            logger.info(f"[MCP TOOL CALL] mcp_update_deprecation({urn}, note='{note}')")
            return True
        return False

    def mcp_patch_sql(self, urn: str, new_sql: str) -> bool:
        """MCP Tool: mcp_patch_sql - Patches dataset SQL aspect and restores HEALTHY status"""
        if urn in self.nodes:
            self.nodes[urn]["sql_definition"] = new_sql
            self.nodes[urn]["status"] = "HEALTHY"
            if "INCIDENT_ACTIVE" in self.nodes[urn]["tags"]:
                self.nodes[urn]["tags"].remove("INCIDENT_ACTIVE")
            logger.info(f"[MCP TOOL CALL] mcp_patch_sql({urn}) -> Status restored to HEALTHY")
            return True
        return False

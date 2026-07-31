"""
FastAPI Orchestrator Server for DataGuardian Agent with MCP & OpenRouter LLM Engine.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from backend.datahub.mcp_client import DataHubMCPToolEngine
from backend.sandbox.db_runner import SandboxRunner
from backend.agent.reasoning import DataGuardianAgent

app = FastAPI(title="DataGuardian Agent API (MCP + LLM Engine)", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

datahub_mcp = DataHubMCPToolEngine()
sandbox = SandboxRunner()
agent = DataGuardianAgent(datahub_mcp, sandbox)

class IncidentTriggerRequest(BaseModel):
    root_urn: Optional[str] = "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)"
    scenario_type: Optional[str] = "SCHEMA_DRIFT" # "SCHEMA_DRIFT", "NULL_SPIKE", "TYPE_MISMATCH"

@app.get("/")
def read_root():
    return {"status": "online", "service": "DataGuardian Agent Engine (MCP + Gemma 2 LLM)", "node_count": len(datahub_mcp.nodes)}

@app.get("/api/graph")
def get_graph_state():
    return {
        "nodes": datahub_mcp.nodes,
        "edges": datahub_mcp.lineage_edges
    }

@app.get("/api/thought-stream")
def get_thought_stream():
    return {"thought_stream": agent.thought_stream}

@app.post("/api/trigger-incident")
def trigger_incident(req: IncidentTriggerRequest):
    scenario = req.scenario_type or "SCHEMA_DRIFT"
    
    if scenario == "NULL_SPIKE":
        sandbox.trigger_null_spike()
    elif scenario == "TYPE_MISMATCH":
        sandbox.trigger_type_mismatch()
    else:
        sandbox.trigger_schema_drift()
    
    result = agent.handle_pipeline_incident(req.root_urn, scenario_type=scenario)
    return result

@app.post("/api/reset")
def reset_graph():
    global datahub_mcp, sandbox, agent
    datahub_mcp = DataHubMCPToolEngine()
    sandbox = SandboxRunner()
    agent = DataGuardianAgent(datahub_mcp, sandbox)
    return {"status": "reset_complete"}

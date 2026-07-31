import React, { useState, useEffect } from 'react';
import LineageGraph from './components/LineageGraph';
import AgentThoughtStream from './components/AgentThoughtStream';
import PRPreviewModal from './components/PRPreviewModal';

export default function App() {
  const [graphData, setGraphData] = useState({ nodes: {}, edges: [] });
  const [thoughtStream, setThoughtStream] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [showPRModal, setShowPRModal] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('SCHEMA_DRIFT');

  const fetchGraphState = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/graph');
      if (res.ok) {
        const data = await res.json();
        setGraphData(data);
      }
    } catch (e) {}
  };

  const fetchThoughtStream = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/thought-stream');
      if (res.ok) {
        const data = await res.json();
        setThoughtStream(data.thought_stream || []);
      }
    } catch (e) {}
  };

  useEffect(() => {
    fetchGraphState();
    const interval = setInterval(() => {
      fetchGraphState();
      fetchThoughtStream();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const triggerIncident = async (scenarioType) => {
    setLoading(true);
    setSelectedScenario(scenarioType);
    try {
      const res = await fetch('http://localhost:8000/api/trigger-incident', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          root_urn: 'urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders_v1,PROD)',
          scenario_type: scenarioType
        })
      });
      const data = await res.json();
      setLastResult(data);
      await fetchGraphState();
      await fetchThoughtStream();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const resetState = async () => {
    try {
      await fetch('http://localhost:8000/api/reset', { method: 'POST' });
      setLastResult(null);
      setThoughtStream([]);
      await fetchGraphState();
    } catch (e) {}
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 space-y-8">
      {/* Header Bar */}
      <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-400 bg-clip-text text-transparent">
              🛡️ DataGuardian Agent
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800/50">
              Track 1: Autonomous Work
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            DataOps SRE & Lineage-Aware Autonomous Incident Remediation powered by DataHub MCP
          </p>
        </div>

        {/* Multi-Scenario Triggers */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => triggerIncident('SCHEMA_DRIFT')}
            disabled={loading}
            className="px-3.5 py-2 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-all shadow-md shadow-rose-950/40 flex items-center gap-1.5"
          >
            🚨 1. Schema Drift
          </button>

          <button
            onClick={() => triggerIncident('NULL_SPIKE')}
            disabled={loading}
            className="px-3.5 py-2 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-all shadow-md shadow-amber-950/40 flex items-center gap-1.5"
          >
            ⚠️ 2. Null Spike
          </button>

          <button
            onClick={() => triggerIncident('TYPE_MISMATCH')}
            disabled={loading}
            className="px-3.5 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-all shadow-md shadow-purple-950/40 flex items-center gap-1.5"
          >
            🔀 3. Type Mismatch
          </button>

          <button
            onClick={resetState}
            className="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-lg text-xs font-medium transition-all"
          >
            🔄 Reset
          </button>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main className="space-y-8">
        {/* Lineage Graph */}
        <LineageGraph nodes={graphData.nodes} edges={graphData.edges} />

        {/* Remediation Result Banner */}
        {lastResult && (
          <div className="p-5 bg-indigo-950/40 border border-indigo-800/60 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 font-bold text-lg">✅ [{lastResult.scenario_type}] Autonomous Remediation Complete</span>
                <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 text-xs rounded border border-emerald-800 font-mono">
                  {lastResult.status}
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Created PR: <code className="text-cyan-300 font-mono">{lastResult.pr_info?.pr_title}</code>
              </p>
              <p className="text-xs text-slate-400 font-mono">
                Fixed SQL: {lastResult.fixed_sql}
              </p>
            </div>

            <button
              onClick={() => setShowPRModal(true)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 shrink-0"
            >
              <span>🔍 Inspect PR Diff & Slack Alert</span>
            </button>
          </div>
        )}

        {/* Thought Stream */}
        <AgentThoughtStream thoughts={thoughtStream} />
      </main>

      {/* PR Preview Modal */}
      {showPRModal && (
        <PRPreviewModal
          prInfo={lastResult?.pr_info}
          slackInfo={lastResult?.slack_info}
          onClose={() => setShowPRModal(false)}
        />
      )}
    </div>
  );
}

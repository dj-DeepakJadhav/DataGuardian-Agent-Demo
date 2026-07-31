import React from 'react';

export default function AgentThoughtStream({ thoughts }) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 backdrop-blur-md">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <span className="text-cyan-400">⚡</span> Agent Thought Stream & Reasoning Engine
      </h2>

      <div className="space-y-3 font-mono text-xs max-h-[380px] overflow-y-auto pr-2 custom-scrollbar">
        {thoughts && thoughts.length > 0 ? (
          thoughts.map((item, idx) => (
            <div key={idx} className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-lg flex items-start gap-3">
              <span className="text-slate-500 shrink-0 font-medium">{item.timestamp}</span>
              <div className="flex-1">
                <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800/40 mb-1">
                  {item.step}
                </span>
                <p className="text-slate-200 mt-0.5">{item.message}</p>

                {item.metadata && Object.keys(item.metadata).length > 0 && (
                  <pre className="mt-2 p-2 bg-slate-900 text-slate-400 rounded text-[11px] overflow-x-auto border border-slate-800">
                    {JSON.stringify(item.metadata, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="text-slate-500 italic p-4 text-center">
            No active incident logs. Click "Simulate Upstream Failure" to trigger autonomous agent reasoning.
          </div>
        )}
      </div>
    </div>
  );
}

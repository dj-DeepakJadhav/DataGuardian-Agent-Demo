import React from 'react';

export default function LineageGraph({ nodes, edges }) {
  const nodeArray = Object.entries(nodes || {});

  const getStatusColor = (status) => {
    switch (status) {
      case 'QUARANTINED':
        return 'border-rose-500 bg-rose-950/40 text-rose-300 shadow-lg shadow-rose-950/50';
      case 'HEALTHY':
        return 'border-emerald-500 bg-emerald-950/30 text-emerald-300 shadow-lg shadow-emerald-950/50';
      default:
        return 'border-slate-700 bg-slate-900 text-slate-300';
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 backdrop-blur-md">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
            DataHub Live Lineage & Blast Radius Graph
          </h2>
          <p className="text-xs text-slate-400 mt-1">Real-time metadata graph traversal & quarantine status</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Healthy Node
          </div>
          <div className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span> Quarantined Node
          </div>
        </div>
      </div>

      {/* Graph Node Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative">
        {nodeArray.map(([urn, details], idx) => (
          <div
            key={urn}
            className={`p-4 rounded-xl border transition-all duration-300 relative ${getStatusColor(details.status)}`}
          >
            <div className="flex items-center justify-between text-xs font-mono mb-2">
              <span className="uppercase text-[10px] px-2 py-0.5 rounded bg-slate-950/60 border border-slate-800 text-slate-400 font-medium">
                {details.platform}
              </span>
              <span className={`px-2 py-0.5 rounded font-semibold text-[10px] ${
                details.status === 'QUARANTINED' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}>
                {details.status}
              </span>
            </div>

            <h3 className="font-mono text-sm font-semibold text-white truncate mb-1" title={details.name}>
              {details.name}
            </h3>

            <p className="text-xs text-slate-400 mb-3 truncate">Owner: {details.owner}</p>

            <div className="flex flex-wrap gap-1">
              {details.tags?.map((tag) => (
                <span key={tag} className="text-[10px] px-2 py-0.5 bg-slate-950/50 border border-slate-800 text-slate-400 rounded">
                  #{tag}
                </span>
              ))}
            </div>

            {idx < nodeArray.length - 1 && (
              <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10 text-slate-600 font-bold">
                ➔
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

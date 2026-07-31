import React from 'react';

export default function PRPreviewModal({ prInfo, slackInfo, onClose }) {
  if (!prInfo) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold"
        >
          ✕
        </button>

        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-950 text-purple-300 border border-purple-800">
              PR Preview
            </span>
            <span className="text-xs text-slate-400 font-mono">{prInfo.branch}</span>
          </div>
          <h2 className="text-xl font-bold text-white">{prInfo.pr_title}</h2>
        </div>

        {/* Slack Alert Simulation */}
        {slackInfo && (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-cyan-400">💬 Simulated Slack Webhook Notification</span>
              <span>{slackInfo.channel}</span>
            </div>
            <p className="text-xs text-slate-200">{slackInfo.message}</p>
          </div>
        )}

        {/* Patch Summary */}
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Agent Rationale</h3>
          <p className="text-xs bg-slate-950 p-3 rounded-lg border border-slate-800 text-emerald-300 font-mono">
            {prInfo.patch_summary}
          </p>
        </div>

        {/* Diff View */}
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Git Patch Diff</h3>
          <pre className="text-xs font-mono p-4 bg-slate-950 rounded-xl border border-slate-800 text-slate-300 overflow-x-auto whitespace-pre-wrap">
            {prInfo.diff}
          </pre>
        </div>

        <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg"
          >
            Close
          </button>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5"
          >
            <span>View on GitHub</span> ➔
          </a>
        </div>
      </div>
    </div>
  );
}

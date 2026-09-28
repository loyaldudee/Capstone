import React from 'react';

export default function Sidebar({ activeTab, setActiveTab, onOpenBenchmark, stats }) {
  const navItems = [
    { id: 'claims', icon: 'table_chart', label: 'Claims Queue & Explorer' },
    { id: 'ingest', icon: 'stream', label: 'Kafka Stream Portal' },
  ];

  const secondaryItems = [
    { icon: 'analytics', label: 'Benchmark Evaluation', onClick: onOpenBenchmark },
    { icon: 'folder_special', label: 'Forensic Dossier', disabled: true },
    { icon: 'account_tree', label: 'Agent Orchestration', disabled: true },
  ];

  return (
    <aside className="fixed left-0 top-14 bottom-0 w-56 bg-surface-container-lowest z-40 flex flex-col justify-between py-space-md px-space-xs border-r border-outline-variant/20 shadow-sm">
      <div className="flex flex-col gap-space-md">
        <div className="px-space-md">
          <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-[10px]">
            Workspace Operations
          </span>
        </div>

        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-space-sm px-space-md py-space-sm rounded-xl transition-all text-left w-full text-[13px] ${
                activeTab === item.id
                  ? 'bg-primary-container text-on-primary-container font-semibold shadow-sm'
                  : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}

          {/* Divider */}
          <div className="mx-space-md my-1 border-t border-outline-variant/20" />

          {secondaryItems.map((item, idx) => (
            <button
              key={idx}
              onClick={item.onClick || undefined}
              disabled={item.disabled}
              className="flex items-center gap-space-sm px-space-md py-space-sm rounded-xl text-[13px] text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors text-left w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className={`material-symbols-outlined text-[18px] ${item.icon === 'analytics' ? 'text-tertiary' : ''}`}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          ))}

          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-space-sm px-space-md py-space-sm rounded-xl text-[13px] text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors text-left w-full"
          >
            <span className="material-symbols-outlined text-[18px]">terminal</span>
            <span>REST API Docs</span>
          </a>
        </nav>
      </div>

      {/* System Telemetry Buffer State Card */}
      <div className="p-space-md mx-1 rounded-xl bg-surface-container-low flex flex-col gap-space-xs border border-outline-variant/20">
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-on-surface-variant uppercase font-semibold tracking-wider">
            Buffer State
          </span>
          <span className="px-space-xs py-[2px] rounded text-[10px] font-bold bg-primary-container text-on-primary-container">
            OPTIMAL
          </span>
        </div>
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-on-surface-variant">Cluster Latency</span>
          <span className="font-code-num font-bold text-on-surface">14ms</span>
        </div>
        <div className="w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
          <div className="bg-primary h-full rounded-full w-[82%] transition-all duration-700" />
        </div>
        <div className="flex items-center justify-between text-[10px] text-on-surface-variant pt-1 border-t border-outline-variant/15 mt-0.5">
          <span>Active Claims</span>
          <span className="font-bold text-on-surface">{stats ? stats.total_claims.toLocaleString() : '...'}</span>
        </div>
      </div>
    </aside>
  );
}

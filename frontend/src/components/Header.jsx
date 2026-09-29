import React from 'react';

export default function Header({ activeTab, setActiveTab, onOpenBenchmark }) {
  return (
    <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-lowest/95 backdrop-blur-xl shadow-sm z-50 flex items-center justify-between px-space-md lg:px-space-lg border-b border-outline-variant/30">
      {/* Brand & Subtitle */}
      <div className="flex items-center gap-space-sm shrink-0">
        <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center shadow-sm">
          <span className="material-symbols-outlined text-primary text-[20px]">shield</span>
        </div>
        <div className="flex flex-col leading-tight">
          <div className="flex items-center gap-1.5">
            <span className="text-primary tracking-tight font-bold text-sm">
              Aegis Claims Intelligence
            </span>
            <span className="hidden sm:inline-block px-1.5 py-[2px] rounded text-[9px] font-bold bg-primary/10 text-primary uppercase tracking-wider">
              Aetheric v4.2
            </span>
          </div>
          <span className="text-[10px] text-on-surface-variant hidden md:inline">
            Forensic Claims Investigation &amp; Streaming Engine
          </span>
        </div>
      </div>

      {/* Top Nav Tabs */}
      <nav className="flex items-center gap-1 sm:gap-2">
        <button
          onClick={() => setActiveTab('claims')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl transition-all text-[12px] font-medium ${
            activeTab === 'claims'
              ? 'bg-primary-container text-on-primary-container font-bold shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">table_chart</span>
          <span>Claims Explorer</span>
        </button>

        <button
          onClick={() => setActiveTab('search')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl transition-all text-[12px] font-medium ${
            activeTab === 'search'
              ? 'bg-primary-container text-on-primary-container font-bold shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">manage_search</span>
          <span>Search Claims</span>
        </button>

        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl transition-all text-[12px] font-medium ${
            activeTab === 'chat'
              ? 'bg-primary-container text-on-primary-container font-bold shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">smart_toy</span>
          <span>AI Adjuster Chat</span>
        </button>

        <button
          onClick={() => setActiveTab('ingest')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl transition-all text-[12px] font-medium ${
            activeTab === 'ingest'
              ? 'bg-primary-container text-on-primary-container font-bold shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">stream</span>
          <span>Kafka Stream Portal</span>
        </button>

        <button
          onClick={onOpenBenchmark}
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[12px] font-medium text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
        >
          <span className="material-symbols-outlined text-[16px] text-tertiary">analytics</span>
          <span>Benchmark Eval</span>
          <span className="font-code-num font-bold text-[10px] bg-tertiary/15 text-tertiary px-1 py-0.5 rounded">0.947</span>
        </button>

        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[12px] font-medium text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
        >
          <span className="material-symbols-outlined text-[16px]">terminal</span>
          <span>API Docs</span>
        </a>
      </nav>

      {/* Senior Adjuster Profile */}
      <div className="flex items-center gap-space-sm shrink-0">
        <div className="hidden sm:flex items-center gap-space-xs bg-surface-container px-space-sm py-1 rounded-full border border-outline-variant/20">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          <span className="text-[11px] text-on-surface-variant font-medium">
            JD - Senior Adjuster
          </span>
        </div>
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-sm text-on-primary">
          <span className="material-symbols-outlined text-[18px]">person</span>
        </div>
      </div>
    </header>
  );
}

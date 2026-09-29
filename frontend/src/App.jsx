import React, { useState, useEffect, useCallback } from 'react';
import './index.css';
import './App.css';
import Header from './components/Header';
import KpiCards from './components/KpiCards';
import ClaimsTable from './components/ClaimsTable';
import ClaimDossier from './components/ClaimDossier';
import KafkaStreamPortal from './components/KafkaStreamPortal';
import SearchClaims from './components/SearchClaims';
import ChatAssistant from './components/ChatAssistant';
import BenchmarkModal from './components/BenchmarkModal';
import { fetchStats, fetchClaims, fetchClaimDossier } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      if (window.location.pathname === '/ingest') return 'ingest';
      if (window.location.pathname === '/search') return 'search';
      if (window.location.pathname === '/chat') return 'chat';
    }
    return 'claims';
  });
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (typeof window !== 'undefined') {
      const path = tab === 'ingest' ? '/ingest' : tab === 'search' ? '/search' : tab === 'chat' ? '/chat' : '/';
      window.history.pushState(null, '', path);
    }
  };

  // Stats
  const [stats, setStats] = useState(null);

  // Claims Table State
  const [claims, setClaims] = useState([]);
  const [totalClaims, setTotalClaims] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 25;
  const [query, setQuery] = useState('');
  const [policyType, setPolicyType] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loadingClaims, setLoadingClaims] = useState(false);

  // Claim Dossier State
  const [selectedClaimId, setSelectedClaimId] = useState(null);
  const [dossier, setDossier] = useState(null);
  const [loadingDossier, setLoadingDossier] = useState(false);

  // Load KPI Stats
  const loadStats = useCallback(async () => {
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (err) {
      console.error('Stats error:', err);
    }
  }, []);

  // Load Claims List
  const loadClaims = useCallback(async () => {
    try {
      setLoadingClaims(true);
      const data = await fetchClaims({
        page,
        limit,
        query,
        policyType,
        status: statusFilter,
      });
      setClaims(data.claims || []);
      setTotalClaims(data.total || 0);

      // If no claim is selected, pick first
      if (data.claims && data.claims.length > 0 && !selectedClaimId) {
        setSelectedClaimId(data.claims[0].claim_id);
      }
    } catch (err) {
      console.error('Claims load error:', err);
    } finally {
      setLoadingClaims(false);
    }
  }, [page, limit, query, policyType, statusFilter, selectedClaimId]);

  // Load Specific Claim Dossier
  const loadDossier = useCallback(async (claimId) => {
    if (!claimId) return;
    try {
      setLoadingDossier(true);
      const data = await fetchClaimDossier(claimId);
      setDossier(data);
    } catch (err) {
      console.error('Dossier load error:', err);
    } finally {
      setLoadingDossier(false);
    }
  }, []);

  // Initial Load & Polling
  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000);
    return () => clearInterval(interval);
  }, [loadStats]);

  useEffect(() => {
    loadClaims();
  }, [loadClaims]);

  useEffect(() => {
    if (selectedClaimId) {
      loadDossier(selectedClaimId);
    }
  }, [selectedClaimId, loadDossier]);

  return (
    <div className="min-h-screen bg-background text-on-surface antialiased">
      {/* Fixed Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        onOpenBenchmark={() => setIsBenchmarkOpen(true)}
      />

      {/* Main Content Area */}
      <div className="w-full">
        <main className="w-full max-w-[1780px] mx-auto pt-14 px-space-md sm:px-space-lg pb-space-xl bg-background min-h-screen">
          <div className="flex flex-col w-full pt-space-md gap-space-md">
            {/* Top Forensic Status Banner */}
            <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-space-sm bg-surface-container-lowest p-space-md rounded-xl shadow-sm border border-outline-variant/30">
              <div className="flex flex-col gap-1">
                <div className="flex flex-wrap items-center gap-space-sm text-xs">
                  <div className="flex items-center gap-space-xs bg-primary/10 text-primary px-space-sm py-[2px] rounded-full">
                    <span className="inline-block w-2 h-2 rounded-full bg-primary animate-pulse" />
                    <span className="font-label-sm uppercase font-bold tracking-wider text-[11px]">
                      Live Ingestion Telemetry
                    </span>
                  </div>
                  <span className="font-code-num text-on-surface-variant font-semibold text-[11px]">
                    SYS.REV 4.2.89
                  </span>
                  <span className="text-outline-variant">•</span>
                  <span className="font-label-sm text-on-surface-variant text-[11px]">
                    NODE-EU-CENTRAL-01
                  </span>
                </div>
                <h1 className="text-xl font-bold text-on-surface tracking-tight leading-tight">
                  Forensic Claims Intelligence Console
                </h1>
                <p className="text-xs text-on-surface-variant max-w-2xl leading-relaxed">
                  Automated multi-agent graph triage &amp; neural vector similarity scanner operating over COIL-2000 distribution streams.
                </p>
              </div>

              {/* Badges on right of banner */}
              <div className="flex flex-wrap items-center gap-space-sm text-xs shrink-0">
                <div className="flex items-center gap-space-xs bg-surface-container-low px-3 py-1.5 rounded-xl border border-outline-variant/30">
                  <span className="material-symbols-outlined text-primary text-[16px]">verified</span>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-on-surface-variant uppercase font-semibold leading-none">Model Performance</span>
                    <span className="font-code-num font-bold text-on-surface text-[11px]">ROC-AUC: 0.9467</span>
                  </div>
                </div>

                <div className="flex items-center gap-space-xs bg-[#B2EAD3]/30 px-3 py-1.5 rounded-xl border border-[#B2EAD3]/50">
                  <span className="material-symbols-outlined text-[#154B35] text-[16px]">dataset</span>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[#154B35] uppercase font-bold leading-none">ChromaDB Sync</span>
                    <span className="font-code-num font-bold text-[#154B35] text-[11px]">ACTIVE (1,800 Vecs)</span>
                  </div>
                </div>

                <div className="flex items-center gap-space-xs bg-primary-container text-on-primary-container px-3 py-1.5 rounded-xl shadow-sm">
                  <span className="material-symbols-outlined text-[16px]">hub</span>
                  <div className="flex flex-col">
                    <span className="text-[10px] uppercase font-bold leading-none">LangGraph Bus</span>
                    <span className="font-code-num font-bold text-[11px]">6-Agent Mesh OK</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 6 KPI Cards Deck */}
            <KpiCards stats={stats} />

            {/* Tab Views */}
            {activeTab === 'claims' && (
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-space-lg items-start">
                {/* Left 5 Columns: Claims Queue Explorer (matches mockup layout) */}
                <div className="xl:col-span-5 flex flex-col gap-space-md">
                  <ClaimsTable
                    claims={claims}
                    total={totalClaims}
                    page={page}
                    limit={limit}
                    setPage={setPage}
                    query={query}
                    setQuery={setQuery}
                    policyType={policyType}
                    setPolicyType={setPolicyType}
                    statusFilter={statusFilter}
                    setStatusFilter={setStatusFilter}
                    selectedClaimId={selectedClaimId}
                    onSelectClaim={(id) => setSelectedClaimId(id)}
                    loading={loadingClaims}
                  />
                </div>

                {/* Right 7 Columns: Comprehensive Claim Dossier & Human-in-the-Loop */}
                <div className="xl:col-span-7 sticky top-16">
                  <ClaimDossier
                    key={dossier?.claim_id || 'empty'}
                    dossier={dossier}
                    onRefreshDossier={loadDossier}
                    onRefreshStats={loadStats}
                  />
                </div>
              </div>
            )}

            {activeTab === 'search' && (
              <SearchClaims
                onSelectClaim={(claimId) => {
                  setSelectedClaimId(claimId);
                  handleTabChange('claims');
                }}
              />
            )}

            {activeTab === 'chat' && (
              <ChatAssistant
                onSelectClaim={(claimId) => {
                  setSelectedClaimId(claimId);
                  handleTabChange('claims');
                }}
              />
            )}

            {activeTab === 'ingest' && (
              <KafkaStreamPortal onRefreshStats={loadStats} />
            )}
          </div>
        </main>
      </div>

      {/* Benchmark Evaluation Modal */}
      <BenchmarkModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
      />
    </div>
  );
}

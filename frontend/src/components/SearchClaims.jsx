import React, { useState } from 'react';
import { searchSimilarClaims } from '../api';

const SAMPLE_QUERIES = [
  'Multi-vehicle highway collision with severe frontal damage and delayed reporting',
  'Commercial warehouse fire during off-hours with sprinkler system failure',
  'Luxury vehicle reported stolen overnight from secure residential parking',
  'Water pipe burst behind drywall causing major flooring and structural mold',
  'Slip and fall accident in commercial store with disputed witness testimonies',
  'Single car rollover accident with late notification and no official police report',
];

const POLICY_OPTIONS = [
  'ALL',
  'Auto',
  'Commercial Property',
  'Homeowners',
  'Third Party',
  'Life',
];

export default function SearchClaims({ onSelectClaim }) {
  const [queryText, setQueryText] = useState('');
  const [policyType, setPolicyType] = useState('ALL');
  const [topK, setTopK] = useState(5);
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [searchedQuery, setSearchedQuery] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!queryText.trim()) return;

    setSearching(true);
    setErrorMsg('');
    try {
      const data = await searchSimilarClaims({
        queryText: queryText.trim(),
        policyType: policyType === 'ALL' ? '' : policyType,
        topK: Number(topK),
      });
      setResults(data || []);
      setSearchedQuery(queryText.trim());
    } catch (err) {
      console.error('Semantic search error:', err);
      setErrorMsg(err.message || 'ChromaDB vector search failed. Ensure backend vector index is initialized.');
    } finally {
      setSearching(false);
    }
  };

  const handleSelectSample = (sample) => {
    setQueryText(sample);
  };

  const getSimilarityBadge = (score) => {
    const pct = Math.round((score || 0.8) * 100);
    if (pct >= 85) {
      return {
        pct,
        style: 'bg-[#B2EAD3]/40 text-[#154B35] border border-[#B2EAD3]',
        label: 'High Relevance',
      };
    } else if (pct >= 70) {
      return {
        pct,
        style: 'bg-primary-container text-on-primary-container border border-primary/20',
        label: 'Strong Match',
      };
    } else {
      return {
        pct,
        style: 'bg-[#E5B558]/20 text-[#8A6300] border border-[#E5B558]/40',
        label: 'Moderate Match',
      };
    }
  };

  return (
    <div className="flex flex-col gap-space-lg w-full">
      {/* ═══ TOP BANNER ═══ */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-space-sm bg-surface-container-lowest p-space-md rounded-xl shadow-sm border border-outline-variant/30">
        <div className="flex flex-col gap-1">
          <div className="flex flex-wrap items-center gap-space-sm text-xs">
            <div className="flex items-center gap-space-xs bg-[#B2EAD3]/30 text-[#154B35] px-space-sm py-[2px] rounded-full">
              <span className="material-symbols-outlined text-[14px]">dataset</span>
              <span className="font-label-sm uppercase font-bold tracking-wider text-[11px]">
                ChromaDB Dense Neural Index
              </span>
            </div>
            <span className="font-code-num text-on-surface-variant font-semibold text-[11px]">
              all-MiniLM-L6-v2 (384-dim)
            </span>
            <span className="text-outline-variant">•</span>
            <span className="font-label-sm text-on-surface-variant text-[11px]">
              Cosine Distance Metric
            </span>
          </div>
          <h1 className="text-xl font-bold text-on-surface tracking-tight leading-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[24px]">manage_search</span>
            Search Claims via Semantic Vector Space
          </h1>
          <p className="text-xs text-on-surface-variant max-w-3xl leading-relaxed">
            Query across historical and active claim incident narratives using dense semantic embeddings.
            Detect narrative analogies, syndicates, and recurring claims regardless of exact phrasing.
          </p>
        </div>

        {/* Telemetry stats pill */}
        <div className="flex flex-wrap items-center gap-space-sm text-xs shrink-0">
          <div className="flex items-center gap-space-xs bg-surface-container-low px-3 py-1.5 rounded-xl border border-outline-variant/30">
            <span className="material-symbols-outlined text-primary text-[16px]">bolt</span>
            <div className="flex flex-col">
              <span className="text-[10px] text-on-surface-variant uppercase font-semibold leading-none">Search Latency</span>
              <span className="font-code-num font-bold text-on-surface text-[11px]">&lt; 18ms</span>
            </div>
          </div>
          <div className="flex items-center gap-space-xs bg-primary-container text-on-primary-container px-3 py-1.5 rounded-xl shadow-sm">
            <span className="material-symbols-outlined text-[16px]">travel_explore</span>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase font-bold leading-none">Index Status</span>
              <span className="font-code-num font-bold text-[11px]">Live Vector DB</span>
            </div>
          </div>
        </div>
      </div>

      {/* ═══ SEARCH CONTROLS PANEL ═══ */}
      <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md">
        <form onSubmit={handleSearch} className="flex flex-col gap-space-md">
          {/* Main Search Input */}
          <div className="relative flex items-center">
            <span className="material-symbols-outlined absolute left-3 text-on-surface-variant text-[22px] pointer-events-none">
              search
            </span>
            <input
              type="text"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="Describe the claim incident, damage, circumstances, or narrative to search semantically..."
              className="w-full pl-10 pr-24 py-3 bg-surface-container-low rounded-xl border border-outline-variant/30 text-on-surface text-[14px] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/60"
            />
            {queryText && (
              <button
                type="button"
                onClick={() => setQueryText('')}
                className="absolute right-3 p-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            )}
          </div>

          {/* Filter Row & Submit Button */}
          <div className="flex flex-wrap items-center justify-between gap-space-sm">
            <div className="flex flex-wrap items-center gap-space-md">
              {/* Policy Type Filter */}
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-semibold text-on-surface-variant">Policy Type:</span>
                <select
                  value={policyType}
                  onChange={(e) => setPolicyType(e.target.value)}
                  className="px-2.5 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant/30 text-[12px] font-medium text-on-surface focus:outline-none focus:border-primary"
                >
                  {POLICY_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>

              {/* Top K Selector */}
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-semibold text-on-surface-variant">Results (Top-K):</span>
                <select
                  value={topK}
                  onChange={(e) => setTopK(e.target.value)}
                  className="px-2.5 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant/30 text-[12px] font-medium text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value={5}>Top 5</option>
                  <option value={10}>Top 10</option>
                  <option value={15}>Top 15</option>
                  <option value={25}>Top 25</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={searching || !queryText.trim()}
              className="px-5 py-2.5 rounded-xl bg-primary text-on-primary font-semibold text-[13px] hover:bg-primary/90 transition-all flex items-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {searching ? (
                <>
                  <span className="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
                  <span>Scanning ChromaDB...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">troubleshoot</span>
                  <span>Execute Vector Search</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Sample Prompt Chips */}
        <div className="flex flex-col gap-1.5 pt-2 border-t border-outline-variant/15">
          <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider">
            Suggested Forensic Search Queries:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {SAMPLE_QUERIES.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSample(sample)}
                className="text-left text-[11px] px-2.5 py-1 rounded-lg bg-surface-container-low hover:bg-surface-container text-on-surface-variant hover:text-primary border border-outline-variant/20 transition-all"
              >
                "{sample}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ═══ ERROR MESSAGE ═══ */}
      {errorMsg && (
        <div className="p-space-md rounded-xl bg-error-container/40 text-on-error-container border border-error/20 flex items-center gap-2 text-[12px]">
          <span className="material-symbols-outlined text-error text-[18px]">error</span>
          <span>{errorMsg}</span>
        </div>
      )}

      {/* ═══ SEARCH RESULTS SECTION ═══ */}
      {searchedQuery && !searching && (
        <div className="flex flex-col gap-space-md">
          {/* Results Summary Header */}
          <div className="flex items-center justify-between text-xs text-on-surface-variant px-1">
            <span className="font-medium">
              Found <strong className="text-on-surface">{results.length}</strong> semantic matches for &ldquo;{searchedQuery}&rdquo;
            </span>
            <span className="text-[11px]">Ranked by dense cosine vector similarity</span>
          </div>

          {results.length === 0 ? (
            <div className="bg-surface-container-lowest rounded-xl p-space-xl text-center border border-outline-variant/20 flex flex-col items-center justify-center">
              <span className="material-symbols-outlined text-on-surface-variant text-[36px] mb-2">
                sentiment_dissatisfied
              </span>
              <p className="text-sm font-semibold text-on-surface">No similar claims found</p>
              <p className="text-xs text-on-surface-variant mt-1">
                Try broadening your query keywords or changing the Policy Type filter to 'ALL'.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
              {results.map((r, idx) => {
                const badge = getSimilarityBadge(r.similarity_score);
                return (
                  <div
                    key={r.claim_id || idx}
                    className="bg-surface-container-lowest p-space-md rounded-xl shadow-sm border border-outline-variant/20 hover:border-primary/40 hover:shadow-md transition-all flex flex-col justify-between gap-space-sm group"
                  >
                    {/* Card Top Row */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2">
                          <span className="font-code-num text-sm font-bold text-primary group-hover:underline">
                            {r.claim_id}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-surface-container text-on-surface-variant">
                            {r.policy_type || 'General'}
                          </span>
                        </div>
                        {r.incident_type && (
                          <span className="text-[11px] text-on-surface-variant font-medium mt-0.5">
                            {r.incident_type} {r.incident_severity ? `• ${r.incident_severity}` : ''}
                          </span>
                        )}
                      </div>

                      {/* Similarity Pill */}
                      <div className={`px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1 shrink-0 ${badge.style}`}>
                        <span className="material-symbols-outlined text-[14px]">insights</span>
                        <span>{badge.pct}% Match</span>
                      </div>
                    </div>

                    {/* Incident Description */}
                    <div className="bg-surface-container-low/60 p-2.5 rounded-lg border border-outline-variant/10">
                      <p className="text-[12px] text-on-surface leading-relaxed line-clamp-3">
                        &ldquo;{r.incident_description}&rdquo;
                      </p>
                    </div>

                    {/* Metadata & Inspect CTA */}
                    <div className="flex items-center justify-between pt-2 border-t border-outline-variant/15 text-[11px] text-on-surface-variant">
                      <div className="flex items-center gap-space-sm flex-wrap">
                        {r.claim_amount != null && (
                          <span className="font-semibold text-on-surface">
                            €{Number(r.claim_amount || 0).toLocaleString()}
                          </span>
                        )}
                        {r.reporting_delay_days != null && (
                          <span>Lag: {r.reporting_delay_days}d</span>
                        )}
                        {r.police_report_filed && (
                          <span>Police: {r.police_report_filed}</span>
                        )}
                      </div>

                      {onSelectClaim && (
                        <button
                          type="button"
                          onClick={() => onSelectClaim(r.claim_id)}
                          className="px-2.5 py-1 rounded-lg bg-primary-container text-on-primary-container hover:bg-primary hover:text-on-primary transition-all font-semibold text-[11px] flex items-center gap-1"
                        >
                          <span>Open Dossier</span>
                          <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ═══ INITIAL EMPTY PROMPT ═══ */}
      {!searchedQuery && !searching && (
        <div className="bg-surface-container-lowest rounded-xl p-space-xl text-center border border-outline-variant/20 flex flex-col items-center justify-center text-on-surface-variant py-16">
          <div className="w-14 h-14 rounded-2xl bg-primary-container flex items-center justify-center text-primary mb-3 shadow-sm">
            <span className="material-symbols-outlined text-[28px]">search_insights</span>
          </div>
          <h3 className="text-base font-bold text-on-surface">
            Ready to Query ChromaDB Vector Store
          </h3>
          <p className="text-xs max-w-md mt-1 leading-relaxed">
            Enter any incident narrative, damage pattern, or suspicious claim scenario above to discover
            semantically related claims across the entire database.
          </p>
        </div>
      )}
    </div>
  );
}

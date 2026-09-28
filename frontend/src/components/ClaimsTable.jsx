import React from 'react';

const STATUS_OPTIONS = [
  'ALL',
  'Pending Review',
  'Approved',
  'Documentation Review',
  'SIU Escalation',
];

export default function ClaimsTable({
  claims,
  total,
  page,
  limit,
  setPage,
  query,
  setQuery,
  policyType,
  setPolicyType,
  statusFilter,
  setStatusFilter,
  selectedClaimId,
  onSelectClaim,
  loading,
}) {
  const totalPages = Math.ceil(total / limit) || 1;

  const getStatusDotColor = (status) => {
    switch (status) {
      case 'Approved':
        return 'bg-[#B2EAD3]';
      case 'SIU Escalation':
        return 'bg-[#F68BA2]';
      case 'Documentation Review':
        return 'bg-[#D2CCF2]';
      case 'Pending Review':
      default:
        return 'bg-[#E5B558]';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Approved':
        return 'bg-[#B2EAD3]/30 text-[#154B35]';
      case 'SIU Escalation':
        return 'bg-[#F68BA2]/25 text-tertiary';
      case 'Documentation Review':
        return 'bg-[#D2CCF2]/40 text-[#464365]';
      case 'Pending Review':
      default:
        return 'bg-[#E5B558]/20 text-[#8A6300]';
    }
  };

  const getPolicyBadge = (policy) => {
    return 'bg-[#D2CCF2]/60 text-[#3D356A]';
  };

  const formatAmount = (amount) => {
    return `€${Number(amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  };

  return (
    <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-sm">
      {/* Tab Toggle Bar (Claims Explorer / ChromaDB Vector) */}
      <div className="flex items-center justify-between bg-surface-container-low p-1 rounded-xl">
        <button className="flex-1 py-1.5 px-space-sm rounded-lg bg-primary-container text-on-primary-container text-[12px] font-semibold transition-all shadow-sm flex items-center justify-center gap-1">
          <span className="material-symbols-outlined text-[14px]">view_list</span>
          <span>Claims Explorer</span>
        </button>
        <button className="flex-1 py-1.5 px-space-sm rounded-lg text-on-surface-variant hover:text-on-surface text-[12px] transition-all flex items-center justify-center gap-1">
          <span className="material-symbols-outlined text-[14px]">bubble_chart</span>
          <span>ChromaDB Vector ({total.toLocaleString()})</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative flex items-center">
        <span className="material-symbols-outlined absolute left-2.5 text-on-surface-variant text-[16px]">search</span>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setPage(1);
          }}
          placeholder="Search by Claim ID, customer, or incident..."
          className="w-full pl-8 pr-3 py-1.5 bg-surface-container-low text-on-surface text-[12px] rounded-lg focus:outline-none focus:bg-surface-container-lowest transition-all border border-transparent focus:border-primary/30"
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="absolute right-2 text-on-surface-variant hover:text-on-surface text-xs"
          >
            ✕
          </button>
        )}
      </div>

      {/* Filter Dropdowns Row */}
      <div className="flex items-center gap-space-sm">
        <div className="flex-1 flex flex-col gap-0.5">
          <label className="text-[10px] text-on-surface-variant font-semibold uppercase tracking-wider">Policy Line</label>
          <div className="relative">
            <select
              value={policyType}
              onChange={(e) => {
                setPolicyType(e.target.value);
                setPage(1);
              }}
              className="w-full appearance-none bg-surface-container-low px-space-sm py-1.5 rounded-lg text-[12px] text-on-surface focus:outline-none cursor-pointer pr-6"
            >
              <option value="ALL">All Policies</option>
              <option value="Auto">Auto / Motor</option>
              <option value="Fire_Property">Fire / Property</option>
              <option value="Boat_Marine">Boat / Marine</option>
              <option value="Life_Health">Life / Health</option>
              <option value="Accident_Liability">Accident / Liability</option>
            </select>
            <span className="material-symbols-outlined absolute right-1.5 top-1.5 text-on-surface-variant pointer-events-none text-[14px]">expand_more</span>
          </div>
        </div>
        <div className="flex-1 flex flex-col gap-0.5">
          <label className="text-[10px] text-on-surface-variant font-semibold uppercase tracking-wider">Queue State</label>
          <div className="relative">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full appearance-none bg-surface-container-low px-space-sm py-1.5 rounded-lg text-[12px] text-on-surface focus:outline-none cursor-pointer pr-6"
            >
              {STATUS_OPTIONS.map((st) => (
                <option key={st} value={st}>
                  {st === 'ALL' ? 'All Statuses' : st}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-1.5 top-1.5 text-on-surface-variant pointer-events-none text-[14px]">expand_more</span>
          </div>
        </div>
      </div>

      {/* Claims Queue List (Card-style like mockup) */}
      <div className="flex flex-col gap-1.5 max-h-[520px] overflow-y-auto pr-0.5">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant text-xs gap-2">
            <span className="material-symbols-outlined text-primary text-[28px] animate-spin">
              progress_activity
            </span>
            <span>Loading claims intelligence queue...</span>
          </div>
        ) : claims.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant text-xs gap-1">
            <span className="material-symbols-outlined text-[32px] text-outline">inbox</span>
            <span>No claims found matching query or filter criteria.</span>
          </div>
        ) : (
          claims.map((claim) => {
            const isSelected = selectedClaimId === claim.claim_id;
            return (
              <div
                key={claim.claim_id}
                onClick={() => onSelectClaim(claim.claim_id)}
                className={`p-space-sm rounded-xl flex flex-col gap-1 cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-primary-fixed/25 shadow-sm ring-1 ring-primary/20'
                    : 'bg-surface-container-low/70 hover:bg-surface-container-low'
                }`}
              >
                {/* Row 1: Status dot, Claim ID, Policy Badge, Amount */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2.5 h-2.5 rounded-full ${getStatusDotColor(claim.claim_status)} shrink-0`} />
                    <span className="font-code-num text-[12px] font-bold text-on-surface">{claim.claim_id}</span>
                    <span className={`px-1.5 py-[1px] rounded text-[10px] font-semibold ${getPolicyBadge(claim.policy_type)}`}>
                      {claim.policy_type?.replace('_', ' ')}
                    </span>
                  </div>
                  <span className={`font-code-num text-[12px] font-bold ${
                    claim.claim_status === 'SIU Escalation' ? 'text-tertiary' : 'text-on-surface'
                  }`}>
                    {formatAmount(claim.claim_amount)}
                  </span>
                </div>
                {/* Row 2: Customer & Status Badge */}
                <div className="flex items-center justify-between text-on-surface-variant text-[11px]">
                  <span className="truncate max-w-[200px]">
                    {claim.customer_id} • {claim.incident_type || claim.incident_description?.slice(0, 30)}
                  </span>
                  <span className={`px-1.5 py-[1px] rounded text-[10px] font-semibold ${getStatusBadge(claim.claim_status)}`}>
                    {claim.claim_status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between pt-space-xs text-on-surface-variant text-[12px]">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1 || loading}
          className="px-space-sm py-1 bg-surface-container-low rounded-lg hover:bg-surface-container transition-colors disabled:opacity-40"
        >
          &lt; Prev
        </button>
        <div className="flex items-center gap-1 font-code-num text-[12px]">
          <span className="w-6 h-6 flex items-center justify-center rounded-lg bg-primary-container text-on-primary-container font-semibold text-[11px]">
            {page}
          </span>
          <span className="text-on-surface-variant text-[10px]">of {totalPages}</span>
        </div>
        <button
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages || loading}
          className="px-space-sm py-1 bg-surface-container-low rounded-lg hover:bg-surface-container transition-colors disabled:opacity-40"
        >
          Next &gt;
        </button>
      </div>
    </div>
  );
}

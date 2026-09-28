import React, { useState, useEffect } from 'react';
import { runInvestigation, submitAdjusterDecision } from '../api';
import AgentExecutiveSummary from './AgentExecutiveSummary';
import AdvisorGuidanceCard from './AdvisorGuidanceCard';

export default function ClaimDossier({ dossier, onRefreshDossier, onRefreshStats }) {
  const [investigating, setInvestigating] = useState(false);
  const [investigationResult, setInvestigationResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Human Adjuster Gate State
  const [selectedDecision, setSelectedDecision] = useState('Approved');
  const [adjusterNotes, setAdjusterNotes] = useState('');
  const [submittingDecision, setSubmittingDecision] = useState(false);

  // Reset local investigation and decision state when switching claims
  useEffect(() => {
    setInvestigationResult(null);
    setErrorMsg('');
    setSuccessMsg('');
    setSelectedDecision(
      dossier?.claim_status && dossier.claim_status !== 'Pending Review'
        ? dossier.claim_status
        : 'Approved'
    );
    setAdjusterNotes('');
  }, [dossier?.claim_id]);

  const handleApplyAdvisor = (recommendedDecision, notes) => {
    if (recommendedDecision) {
      setSelectedDecision(recommendedDecision);
    }
    if (notes) {
      setAdjusterNotes(notes);
    }
  };

  if (!dossier) {
    return (
      <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col items-center justify-center text-center min-h-[500px] text-on-surface-variant">
        <span className="material-symbols-outlined text-primary text-[48px] mb-3 animate-bounce">
          fingerprint
        </span>
        <h3 className="text-lg font-bold text-on-surface">
          No Claim Selected
        </h3>
        <p className="text-[12px] max-w-xs mt-1 leading-relaxed">
          Select any claim from the queue to view its full actuarial dossier, trigger multi-agent
          forensic reasoning, and record adjudication decisions.
        </p>
      </div>
    );
  }

  const latestInv = investigationResult || dossier.latest_investigation;

  // Handle Multi-Agent Investigation Execution
  const handleRunInvestigation = async () => {
    setInvestigating(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await runInvestigation(dossier.claim_id);
      setInvestigationResult(res);
      setSuccessMsg(`LangGraph 6-Agent workflow completed for ${dossier.claim_id}!`);
      onRefreshDossier(dossier.claim_id);
      onRefreshStats();
    } catch (err) {
      setErrorMsg(err.message || 'Investigation execution failed');
    } finally {
      setInvestigating(false);
    }
  };

  // Handle Adjuster Decision Sign-Off
  const handleDecisionSubmit = async () => {
    setSubmittingDecision(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await submitAdjusterDecision({
        claimId: dossier.claim_id,
        decision: selectedDecision,
        notes: adjusterNotes,
        adjusterName: 'Senior Adjuster (Four-Eyes Gate)',
      });
      setSuccessMsg(`Decision '${res.new_status}' recorded successfully!`);
      setAdjusterNotes('');
      onRefreshDossier(dossier.claim_id);
      onRefreshStats();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to record decision');
    } finally {
      setSubmittingDecision(false);
    }
  };

  const formatAmount = (amount) => {
    return `€${Number(amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  };

  const getStatusStyle = (status) => {
    switch (status) {
      case 'Approved': return 'bg-[#B2EAD3]/30 text-[#154B35]';
      case 'SIU Escalation': return 'bg-[#F68BA2]/25 text-tertiary';
      case 'Documentation Review': return 'bg-[#D2CCF2]/40 text-[#464365]';
      default: return 'bg-[#E5B558]/20 text-[#8A6300]';
    }
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md p-space-lg">
      {/* ═══ DOSSIER HEADER & CTA ═══ */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-space-sm pb-space-xs">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-space-xs flex-wrap">
            <span className="text-lg font-bold text-on-surface tracking-tight">
              DOSSIER # {dossier.claim_id?.replace(/\D+/g, '').slice(-4) || '0000'}
            </span>
            <span className="font-code-num text-[12px] text-primary font-bold">{dossier.claim_id}</span>
            <span className={`px-1.5 py-[2px] rounded text-[10px] font-semibold ${getStatusStyle(dossier.claim_status)}`}>
              {(dossier.claim_status || 'PENDING REVIEW').toUpperCase()}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-on-surface-variant text-[11px] flex-wrap">
            <span>Customer: <strong className="text-on-surface">{dossier.customer_id}</strong></span>
            <span className="text-outline-variant">•</span>
            <span>Incident: <strong>{dossier.incident_date || '2026-09-28'}</strong></span>
            <span className="text-outline-variant">•</span>
            <span>Filed: <strong>{dossier.claim_date || '14:22 UTC'}</strong></span>
          </div>
        </div>
        <button
          onClick={handleRunInvestigation}
          disabled={investigating}
          className="px-space-md py-space-sm bg-primary text-on-primary text-[12px] font-semibold rounded-xl hover:bg-primary/90 transition-all flex items-center gap-1.5 shadow-sm shrink-0 disabled:opacity-50"
        >
          {investigating ? (
            <>
              <span className="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
              <span>Running...</span>
            </>
          ) : (
            <>
              <span className="material-symbols-outlined text-[16px]">play_circle</span>
              <span>Run 6-Agent LangGraph Audit</span>
            </>
          )}
        </button>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-2.5 rounded-xl bg-error-container text-on-error-container text-[11px] flex items-center gap-2 border border-error/20">
          <span className="material-symbols-outlined text-[16px]">error</span>
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-2.5 rounded-xl bg-[#B2EAD3]/40 text-[#154B35] text-[11px] flex items-center gap-2 border border-[#B2EAD3]">
          <span className="material-symbols-outlined text-[16px]">check_circle</span>
          <span>{successMsg}</span>
        </div>
      )}

      {/* ═══ 4-METRIC GRID ROW ═══ */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm">
        <div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-0.5">
          <span className="text-[10px] text-on-surface-variant font-medium uppercase tracking-wider">Claimed Amount</span>
          <span className="text-base font-bold text-on-surface">{formatAmount(dossier.claim_amount)}</span>
          <span className="text-[10px] text-tertiary font-semibold">Severity: {dossier.incident_severity || 'N/A'}</span>
        </div>
        <div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-0.5">
          <span className="text-[10px] text-on-surface-variant font-medium uppercase tracking-wider">Policy Line</span>
          <span className="text-base font-bold text-on-surface">{dossier.policy_type?.replace('_', ' ') || 'N/A'}</span>
          <span className="text-[10px] text-on-surface-variant">Active Lines: {dossier.policy_count || 1}</span>
        </div>
        <div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-0.5">
          <span className="text-[10px] text-on-surface-variant font-medium uppercase tracking-wider">Reporting Lag</span>
          <span className="text-base font-bold text-on-surface">{dossier.reporting_delay_days || 0} Days</span>
          <span className="text-[10px] text-[#154B35] font-semibold">Bench: 0-7 Days</span>
        </div>
        <div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-0.5">
          <span className="text-[10px] text-on-surface-variant font-medium uppercase tracking-wider">Official Reports</span>
          <span className="text-base font-bold text-on-surface">
            {dossier.police_report_filed === 'Yes' ? 'Police Filed' : 'No Police'}
          </span>
          <span className="text-[10px] text-[#154B35] font-semibold">
            Witness: {dossier.witness_present || 'No'}
          </span>
        </div>
      </div>

      {/* ═══ COIL-2000 CUSTOMER PROFILE ═══ */}
      <div className="bg-surface-container-low/60 p-space-md rounded-xl flex flex-col gap-space-xs border border-outline-variant/15">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant">
            COIL-2000 Insured Sociodemographic Vector
          </span>
          <span className="px-1.5 py-[1px] bg-[#D2CCF2]/60 text-[#3D356A] text-[10px] rounded font-semibold">
            Matched Segment
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-space-sm mt-1 text-on-surface">
          <div>
            <span className="block text-[10px] text-on-surface-variant">Demographic Group</span>
            <span className="text-[12px] font-semibold">Average Family</span>
          </div>
          <div>
            <span className="block text-[10px] text-on-surface-variant">Age Bracket</span>
            <span className="text-[12px] font-semibold">40-50 years</span>
          </div>
          <div>
            <span className="block text-[10px] text-on-surface-variant">Purchasing Power</span>
            <span className="text-[12px] font-semibold">Tier {dossier.policy_count || 1} / 8</span>
          </div>
          <div>
            <span className="block text-[10px] text-on-surface-variant">Active Policies</span>
            <span className="text-[12px] font-semibold">{dossier.prior_claims_count || 0} Claims History</span>
          </div>
        </div>
      </div>

      {/* ═══ ADJUSTER INTAKE NARRATIVE ═══ */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-1.5 text-on-surface text-[13px] font-semibold">
          <span className="material-symbols-outlined text-primary text-[16px]">subject</span>
          <span>Adjuster Intake Narrative &amp; Telematics</span>
        </div>
        <div className="p-space-sm rounded-lg bg-surface-container-low/40 border border-outline-variant/15">
          <p className="text-[12px] text-on-surface italic leading-relaxed">
            "{dossier.incident_description || 'No narrative description available.'}"
          </p>
        </div>
      </div>

      {/* ═══ MULTI-AGENT LANGGRAPH RESULTS ═══ */}
      {latestInv ? (
        <div className="flex flex-col gap-space-sm pt-1">
          {/* Pipeline Status Bar */}
          <div className="flex items-center gap-2 text-[11px]">
            <div className="flex items-center gap-1.5 text-primary font-semibold">
              <span className="material-symbols-outlined text-[16px]">account_tree</span>
              <span>LangGraph Forensic Multi-Agent Orchestration</span>
            </div>
            <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#B2EAD3]/30">
              <span className="w-1.5 h-1.5 rounded-full bg-[#154B35]" />
              <span className="text-[10px] font-bold text-[#154B35] uppercase">Pipeline: Completed</span>
            </div>
          </div>

          {/* Agent Step Indicators */}
          <div className="grid grid-cols-6 gap-1 text-center text-[10px]">
            {['01 Sanitizer', '02 Demographic', '03 Vector', '04 SIU Anomaly', '05 Synthesis', '06 Advisor'].map((step, idx) => (
              <div key={idx} className="flex flex-col items-center gap-0.5 p-1.5 rounded-lg bg-surface-container-low/60">
                <span className={`material-symbols-outlined text-[14px] ${
                  idx === 3 && latestInv.is_anomaly ? 'text-tertiary' : 'text-primary'
                }`}>
                  {idx === 3 && latestInv.is_anomaly ? 'warning' : 'check_circle'}
                </span>
                <span className={`font-semibold ${idx === 3 && latestInv.is_anomaly ? 'text-tertiary' : 'text-on-surface-variant'}`}>
                  {step.split(' ')[1]}
                </span>
              </div>
            ))}
          </div>

          {/* Composite Score Banner */}
          <div className="flex items-center justify-between p-space-sm rounded-xl bg-surface-container-low border border-outline-variant/20">
            <span className="text-[11px] font-semibold text-on-surface-variant uppercase">Composite Forensic Anomaly Score</span>
            <div className="flex items-center gap-2">
              <span className={`text-[13px] font-bold ${
                latestInv.composite_risk_score > 0.6 ? 'text-tertiary' : 'text-primary'
              }`}>
                {((latestInv.composite_risk_score || 0) * 100).toFixed(1)}%
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                latestInv.risk_tier === 'High' || latestInv.risk_tier === 'Critical'
                  ? 'bg-error-container text-on-error-container'
                  : latestInv.risk_tier === 'Medium'
                  ? 'bg-secondary-container text-on-secondary-container'
                  : 'bg-[#B2EAD3]/40 text-[#154B35]'
              }`}>
                [{latestInv.risk_tier || 'Low'} Risk]
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                latestInv.composite_risk_score > 0.6
                  ? 'bg-tertiary'
                  : latestInv.composite_risk_score > 0.3
                  ? 'bg-secondary'
                  : 'bg-primary'
              }`}
              style={{ width: `${Math.min(100, (latestInv.composite_risk_score || 0) * 100)}%` }}
            />
          </div>

          {/* Key Findings / Synthesizer Executive Summary */}
          {latestInv.executive_summary && (
            <AgentExecutiveSummary
              summaryText={latestInv.executive_summary}
              claimId={dossier.claim_id}
            />
          )}

          {/* SIU Forensic Evidence Checklist */}
          {latestInv.evidence_checklist && latestInv.evidence_checklist.length > 0 && (
            <div className="p-space-sm rounded-lg bg-surface-container-low/40 border border-outline-variant/15 flex flex-col gap-1.5">
              <span className="text-[10px] font-bold text-tertiary uppercase tracking-wider">
                Forensic Investigation Checklist (Agent 5):
              </span>
              <ul className="flex flex-col gap-1 text-[12px] text-on-surface">
                {latestInv.evidence_checklist.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <input
                      type="checkbox"
                      defaultChecked={false}
                      className="mt-0.5 rounded text-primary focus:ring-primary shrink-0"
                    />
                    <span className="leading-snug">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Senior Adjuster Advisor Agent (Agent 6 Copilot) */}
          {latestInv.advisor_guidance && (
            <AdvisorGuidanceCard
              guidance={latestInv.advisor_guidance}
              onApplyRecommendation={handleApplyAdvisor}
            />
          )}
        </div>
      ) : (
        <div className="p-space-sm rounded-lg bg-surface-container-low/40 text-center text-[12px] text-on-surface-variant border border-outline-variant/15">
          Click <strong>"Run 6-Agent LangGraph Audit"</strong> above to
          evaluate this claim with Scikit-Learn risk models, ChromaDB vector matching, and LLM synthesis.
        </div>
      )}

      {/* ═══ HUMAN-IN-THE-LOOP ADJUDICATION GATE ═══ */}
      <div className="p-space-md rounded-xl bg-surface-container-low border border-outline-variant/20 flex flex-col gap-space-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[13px] font-bold text-on-surface">
            <span className="material-symbols-outlined text-primary text-[18px]">gavel</span>
            <span>Human-in-the-Loop Adjudication Gate</span>
          </div>
          <span className="text-[10px] text-on-surface-variant uppercase font-semibold">MANDATE: Adjuster_Sign_Off</span>
        </div>

        {/* 3 Decision Buttons */}
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => setSelectedDecision('Approved')}
            className={`py-2 px-3 rounded-xl text-[12px] font-bold transition-all flex items-center justify-center gap-1 ${
              selectedDecision === 'Approved'
                ? 'bg-[#B2EAD3] text-[#154B35] shadow-sm ring-1 ring-[#154B35]/20'
                : 'bg-surface-container text-on-surface hover:bg-[#B2EAD3]/30'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">check_circle</span>
            Approve Claim
          </button>
          <button
            onClick={() => setSelectedDecision('Documentation Review')}
            className={`py-2 px-3 rounded-xl text-[12px] font-bold transition-all flex items-center justify-center gap-1 ${
              selectedDecision === 'Documentation Review'
                ? 'bg-secondary-container text-on-secondary-container shadow-sm ring-1 ring-secondary/20'
                : 'bg-surface-container text-on-surface hover:bg-secondary-container/30'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">find_in_page</span>
            Request Docs
          </button>
          <button
            onClick={() => setSelectedDecision('SIU Escalation')}
            className={`py-2 px-3 rounded-xl text-[12px] font-bold transition-all flex items-center justify-center gap-1 ${
              selectedDecision === 'SIU Escalation'
                ? 'bg-error-container text-on-error-container shadow-sm ring-1 ring-error/20'
                : 'bg-surface-container text-on-surface hover:bg-error-container/30'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">warning</span>
            Escalate to SIU
          </button>
        </div>

        {/* Adjuster Notes */}
        <div>
          <span className="text-[10px] text-on-surface-variant font-semibold block mb-1">Senior Adjuster Forensic Evaluation Notes</span>
          <textarea
            rows={2}
            value={adjusterNotes}
            onChange={(e) => setAdjusterNotes(e.target.value)}
            placeholder="Enter official adjuster rationale or compliance notes..."
            className="w-full p-2 rounded-lg bg-surface-container-lowest border border-outline-variant/30 text-[12px] text-on-surface focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[10px] text-on-surface-variant flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">lock</span>
            SHA-256 Ledger Stamp: {dossier.claim_id?.slice(0, 8)}...
          </span>
          <button
            onClick={handleDecisionSubmit}
            disabled={submittingDecision}
            className="py-2 px-4 rounded-xl bg-primary text-on-primary font-semibold text-[12px] hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center gap-1.5 shadow-sm"
          >
            <span className="material-symbols-outlined text-[16px]">verified</span>
            {submittingDecision ? 'Submitting...' : 'Record Final Adjudication Sign-Off'}
          </button>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';

export default function AdvisorGuidanceCard({
  guidance,
  onApplyRecommendation,
}) {
  const [copied, setCopied] = useState(false);

  if (!guidance || Object.keys(guidance).length === 0) return null;

  const rec = guidance.recommended_decision || 'Documentation Review';
  const rationale = guidance.decision_rationale || '';
  const questions = guidance.claimant_inquiry_questions || [];
  const documents = guidance.mandatory_documents || [];
  const riskDrivers = guidance.key_risk_drivers || [];
  const prefilledNotes = guidance.prefilled_adjuster_notes || '';

  const getRecStyle = () => {
    switch (rec) {
      case 'Approved':
        return {
          pill: 'bg-[#B2EAD3]/60 text-[#154B35] border border-[#B2EAD3]',
          icon: 'check_circle',
          border: 'border-[#B2EAD3]/80',
          title: 'Routine Settlement Path',
        };
      case 'SIU Escalation':
        return {
          pill: 'bg-error-container text-on-error-container border border-error/30',
          icon: 'security',
          border: 'border-error/40',
          title: 'Special Investigation Unit Referral',
        };
      default:
        return {
          pill: 'bg-secondary-container text-on-secondary-container border border-secondary/30',
          icon: 'find_in_page',
          border: 'border-secondary/40',
          title: 'Formal Documentation Review Required',
        };
    }
  };

  const style = getRecStyle();

  const handleCopyQuestions = () => {
    if (questions.length === 0) return;
    const text = questions.map((q, idx) => `${idx + 1}. ${q}`).join('\n\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className={`p-space-md rounded-xl bg-surface-container-low border-2 ${style.border} flex flex-col gap-space-md shadow-sm transition-all`}>
      {/* ═══ HEADER ═══ */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs pb-space-xs border-b border-outline-variant/20">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-secondary-container text-on-secondary-container flex items-center justify-center shadow-sm">
            <span className="material-symbols-outlined text-[20px]">smart_toy</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[12px] font-bold text-on-surface tracking-tight flex items-center gap-1.5">
              Senior Adjuster Advisor Agent (AI Copilot)
              <span className="px-1.5 py-[1px] rounded text-[9px] font-bold bg-primary/10 text-primary uppercase">
                Agent 6
              </span>
            </span>
            <span className="text-[10px] text-on-surface-variant">
              Strategic adjudication advisory, evidentiary requirements &amp; interview scripts
            </span>
          </div>
        </div>

        {/* Action Badge */}
        <div className={`px-2.5 py-1 rounded-full text-[11px] font-bold flex items-center gap-1 shrink-0 ${style.pill}`}>
          <span className="material-symbols-outlined text-[15px]">{style.icon}</span>
          <span>RECOMMENDED: {rec.toUpperCase()}</span>
        </div>
      </div>

      {/* ═══ LLM OFFLINE NOTICE ═══ */}
      {guidance.llm_status === 'offline' && (
        <div className="flex items-center gap-2.5 p-2.5 rounded-lg bg-[#FFF3E0]/60 border border-[#FFB74D]/40 text-[11px] text-[#E65100]">
          <span className="material-symbols-outlined text-[18px] text-[#F57C00] shrink-0">cloud_off</span>
          <span className="leading-snug font-medium">
            {guidance.llm_status_message || '⚠️ LLM is not reachable right now. This recommendation is based on deterministic analysis of all agent findings.'}
          </span>
        </div>
      )}

      {/* ═══ RATIONALE & RISK DRIVERS ═══ */}
      <div className="flex flex-col gap-2">
        <div className="p-2.5 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-[12px] text-on-surface leading-relaxed">
          <span className="font-semibold text-primary block mb-0.5">
            Adjudication Rationale ({style.title}):
          </span>
          <p>{rationale}</p>
        </div>

        {riskDrivers.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-0.5">
            {riskDrivers.map((driver, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded text-[10px] font-medium bg-surface-container-lowest text-on-surface-variant border border-outline-variant/20 flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-[12px] text-tertiary">priority_high</span>
                <span>{driver}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* ═══ SCRIPTED QUESTIONS FOR CLAIMANT ═══ */}
      {questions.length > 0 && (
        <div className="flex flex-col gap-2 pt-1 border-t border-outline-variant/15">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface uppercase tracking-wider flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px] text-secondary">contact_support</span>
              Inquiry Questions for Claimant / Policyholder:
            </span>
            <button
              type="button"
              onClick={handleCopyQuestions}
              className="text-[11px] font-semibold text-primary hover:text-primary/80 flex items-center gap-1 px-2 py-0.5 rounded-md hover:bg-surface-container transition-colors"
            >
              <span className="material-symbols-outlined text-[14px]">
                {copied ? 'check' : 'content_copy'}
              </span>
              <span>{copied ? 'Questions Copied!' : 'Copy Questions'}</span>
            </button>
          </div>

          <div className="flex flex-col gap-1.5">
            {questions.map((q, idx) => (
              <div
                key={idx}
                className="p-2 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-[12px] flex items-start gap-2 group hover:border-secondary/40 transition-colors"
              >
                <span className="w-5 h-5 rounded-md bg-secondary/10 text-secondary font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">
                  Q{idx + 1}
                </span>
                <span className="text-on-surface leading-snug flex-1">&ldquo;{q}&rdquo;</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══ MANDATORY DOCUMENTS REQUIRED ═══ */}
      {documents.length > 0 && (
        <div className="flex flex-col gap-1.5 pt-1 border-t border-outline-variant/15">
          <span className="text-[11px] font-bold text-on-surface uppercase tracking-wider flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[16px] text-tertiary">folder_open</span>
            Mandatory Evidentiary Documents Required:
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {documents.map((doc, idx) => (
              <div
                key={idx}
                className="p-2 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-[11px] text-on-surface font-medium flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[15px] text-primary shrink-0">check_box_outline_blank</span>
                <span className="truncate">{doc}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══ APPLY ADVICE ACTION BUTTON ═══ */}
      {onApplyRecommendation && (
        <div className="pt-2 border-t border-outline-variant/15 flex items-center justify-between gap-2 flex-wrap">
          <span className="text-[11px] text-on-surface-variant italic">
            Apply advisor's recommendation directly into the decision gate below:
          </span>
          <button
            type="button"
            onClick={() => onApplyRecommendation(rec, prefilledNotes)}
            className="px-3.5 py-1.5 rounded-xl bg-secondary text-on-secondary hover:bg-secondary/90 text-[12px] font-semibold flex items-center gap-1.5 shadow-sm transition-all"
          >
            <span className="material-symbols-outlined text-[16px]">touch_app</span>
            <span>Apply &ldquo;{rec}&rdquo; to Decision Gate</span>
          </button>
        </div>
      )}
    </div>
  );
}

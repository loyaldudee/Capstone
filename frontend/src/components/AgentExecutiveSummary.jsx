import React from 'react';

/**
 * Formats inline bold (**text**), status codes (VALID, INVALID), and currency amounts.
 */
function formatInline(text) {
  if (!text) return null;

  // Split by bold (**...**) first
  const parts = [];
  const boldRegex = /\*\*(.*?)\*\*/g;
  let lastIndex = 0;
  let match;

  while ((match = boldRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    parts.push({ isBold: true, text: match[1] });
    lastIndex = boldRegex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  // Render parts with inline badges for keywords like VALID, INVALID, etc.
  return parts.map((part, pIdx) => {
    if (typeof part === 'string') {
      return renderStyledWords(part, pIdx);
    }
    return (
      <strong key={pIdx} className="font-semibold text-on-surface">
        {renderStyledWords(part.text, `${pIdx}-b`)}
      </strong>
    );
  });
}

function renderStyledWords(str, keyPrefix) {
  // Check for VALID, INVALID, currency
  const tokens = str.split(/(VALID:|INVALID:|€[\d,]+(?:\.\d+)?)/g);
  return tokens.map((token, tIdx) => {
    if (token === 'VALID:') {
      return (
        <span
          key={`${keyPrefix}-${tIdx}`}
          className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#B2EAD3]/60 text-[#154B35] mr-1 align-baseline border border-[#B2EAD3]"
        >
          VALID
        </span>
      );
    }
    if (token === 'INVALID:') {
      return (
        <span
          key={`${keyPrefix}-${tIdx}`}
          className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-error-container text-on-error-container mr-1 align-baseline border border-error/30"
        >
          INVALID
        </span>
      );
    }
    if (token.startsWith('€')) {
      return (
        <span key={`${keyPrefix}-${tIdx}`} className="font-code-num font-semibold text-on-surface">
          {token}
        </span>
      );
    }
    return token;
  });
}

const SECTION_ICONS = {
  synopsis: 'description',
  incident: 'description',
  coverage: 'verified_user',
  policy: 'verified_user',
  risk: 'warning_amber',
  anomaly: 'analytics',
  indicators: 'analytics',
  similarity: 'history',
  historical: 'history',
  recommendation: 'recommend',
};

function getSectionIcon(title) {
  const lower = title.toLowerCase();
  for (const [key, icon] of Object.entries(SECTION_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return 'info';
}

export default function AgentExecutiveSummary({ summaryText, claimId }) {
  if (!summaryText) return null;

  // Extract LLM offline notice if present at the start
  let llmNotice = '';
  let cleanedText = summaryText;
  if (summaryText.startsWith('⚠️')) {
    const noticeEnd = summaryText.indexOf('\n\n');
    if (noticeEnd !== -1) {
      llmNotice = summaryText.substring(0, noticeEnd).replace(/\*\*/g, '').trim();
      cleanedText = summaryText.substring(noticeEnd + 2).trim();
    }
  }

  // Split into raw blocks by double newlines or single newlines followed by markdown headers/numbers
  const rawBlocks = cleanedText
    .split(/\n\s*\n/)
    .map((b) => b.trim())
    .filter(Boolean);

  let briefHeader = '';
  const sections = [];
  const otherBlocks = [];

  rawBlocks.forEach((block) => {
    // Check if it's the header (### Executive Claim Brief: CLM_...)
    if (block.startsWith('### ') || block.startsWith('## ')) {
      briefHeader = block.replace(/^#+\s*/, '').trim();
      return;
    }

    // Check if it's a numbered or bolded section item:
    // e.g., "**1. Incident Synopsis**: Insured filed claim..."
    // or "**Incident Synopsis**: Insured filed claim..."
    const match = block.match(/^\*\*(\d+\.\s*)?([^*:]+)\*\*:\s*([\s\S]*)$/);
    if (match) {
      const numberStr = match[1] ? match[1].replace(/\.\s*$/, '').trim() : '';
      const title = match[2].trim();
      const body = match[3].trim();
      sections.push({
        number: numberStr || String(sections.length + 1),
        title,
        body,
        icon: getSectionIcon(title),
      });
      return;
    }

    // Check if it's a bulleted list
    if (block.startsWith('- ') || block.startsWith('* ')) {
      const items = block
        .split(/\n\s*[-*]\s+/)
        .map((i) => i.replace(/^[-*]\s+/, '').trim())
        .filter(Boolean);
      otherBlocks.push({ type: 'bullets', items });
      return;
    }

    otherBlocks.push({ type: 'text', content: block });
  });

  return (
    <div className="rounded-xl bg-surface-container-low/40 border border-outline-variant/20 p-space-md flex flex-col gap-space-sm">
      {/* Header bar */}
      <div className="flex items-center justify-between pb-2 border-b border-outline-variant/15 flex-wrap gap-1">
        <div className="flex items-center gap-1.5">
          <span className="material-symbols-outlined text-primary text-[18px]">psychology</span>
          <span className="text-[11px] font-bold text-primary uppercase tracking-wider">
            AI Executive Summary (Synthesizer Agent)
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-primary/10 text-primary">
            LangGraph Mesh
          </span>
          {claimId && (
            <span className="font-code-num text-[11px] font-bold text-on-surface-variant bg-surface-container px-2 py-0.5 rounded border border-outline-variant/20">
              {claimId}
            </span>
          )}
        </div>
      </div>

      {/* LLM Offline Notice Banner */}
      {llmNotice && (
        <div className="flex items-center gap-2.5 p-2.5 rounded-lg bg-[#FFF3E0]/60 border border-[#FFB74D]/40 text-[11px] text-[#E65100]">
          <span className="material-symbols-outlined text-[18px] text-[#F57C00] shrink-0">cloud_off</span>
          <span className="leading-snug font-medium">{llmNotice}</span>
        </div>
      )}

      {/* Render Parsed Structured Sections */}
      {sections.length > 0 ? (
        <div className="grid grid-cols-1 gap-2 pt-1">
          {sections.map((sec, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 flex flex-col gap-1.5 shadow-sm transition-all hover:border-primary/30"
            >
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-md bg-primary-container text-primary flex items-center justify-center text-[11px] font-bold shrink-0">
                  {sec.number}
                </span>
                <div className="flex items-center gap-1.5 flex-1 min-w-0">
                  <span className="material-symbols-outlined text-[15px] text-on-surface-variant">
                    {sec.icon}
                  </span>
                  <span className="text-[12px] font-bold text-on-surface tracking-tight truncate">
                    {sec.title}
                  </span>
                </div>
              </div>

              <div className="text-[12px] text-on-surface-variant leading-relaxed pl-7">
                {formatInline(sec.body)}
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {/* Other Blocks (e.g. Freeform paragraphs or bullets if present) */}
      {otherBlocks.map((ob, idx) => {
        if (ob.type === 'bullets') {
          return (
            <ul key={idx} className="flex flex-col gap-1 text-[12px] text-on-surface pl-2">
              {ob.items.map((it, iIdx) => (
                <li key={iIdx} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                  <span className="leading-relaxed">{formatInline(it)}</span>
                </li>
              ))}
            </ul>
          );
        }
        return (
          <p key={idx} className="text-[12px] text-on-surface-variant leading-relaxed">
            {formatInline(ob.content)}
          </p>
        );
      })}
    </div>
  );
}

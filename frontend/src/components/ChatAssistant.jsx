import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, resetChatSession, fetchChatSuggestions } from '../api';

const DEFAULT_SUGGESTIONS = [
  {
    category: 'High Risk & Anomaly',
    prompt: 'Show me the top 5 highest risk claims currently pending review.',
    icon: 'warning',
  },
  {
    category: 'Reporting Delays',
    prompt: 'Which claims have a reporting delay over 30 days and no police report?',
    icon: 'schedule',
  },
  {
    category: 'ChromaDB Precedent',
    prompt: 'Find previous claims involving water leakage while the homeowner was on vacation.',
    icon: 'saved_search',
  },
  {
    category: 'Portfolio Analytics',
    prompt: 'What is our overall claim approval rate, SIU escalation rate, and total claims count?',
    icon: 'analytics',
  },
  {
    category: 'Forensic Deep-Dive',
    prompt: 'Why was claim CLM_DIRTY_002 escalated to SIU? Summarize key forensic flags.',
    icon: 'biotech',
  },
];

export default function ChatAssistant({ onSelectClaim }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `### Welcome to Aegis AI Adjuster Copilot 👋\n\nI am your **Universal Insurance Intelligence Assistant**, equipped with real-time access to the entire claims registry, forensic models, and vector embeddings.\n\nYou can ask me **any natural language question** about claims, anomalies, precedents, or portfolio KPIs. I dynamically execute 4 specialized tools to retrieve factual ground truth without hallucination:\n\n- ⚡ **` + '`query_claims_db`' + `**: Multi-attribute filtering (amounts, delays, policy lines, severity, police reports).\n- 🔍 **` + '`search_incident_precedents`' + `**: Dense vector search across incident narratives in ChromaDB.\n- 📋 **` + '`get_claim_dossier`' + `**: 360° forensic profile, ML risk breakdown, and evidence checklist for any claim.\n- 📊 **` + '`get_system_kpis`' + `**: Portfolio metrics, approval breakdown, and verified ML model benchmarks.\n\n*Click one of the prompt chips below or type any question to start!*`,
      toolsCalled: [],
      referencedClaims: [],
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [suggestions, setSuggestions] = useState(DEFAULT_SUGGESTIONS);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    async function loadSuggestions() {
      try {
        const data = await fetchChatSuggestions();
        if (data && data.suggestions && data.suggestions.length > 0) {
          const mapped = data.suggestions.map((s, idx) => ({
            ...s,
            icon: DEFAULT_SUGGESTIONS[idx % DEFAULT_SUGGESTIONS.length].icon,
          }));
          setSuggestions(mapped);
        }
      } catch (err) {
        console.warn('Using default suggestions:', err);
      }
    }
    loadSuggestions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || inputText).trim();
    if (!text || loading) return;

    const userMessage = {
      role: 'user',
      content: text,
      toolsCalled: [],
      referencedClaims: [],
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      const response = await sendChatMessage({
        message: text,
        sessionId: sessionId,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.reply,
        toolsCalled: response.tools_called || [],
        referencedClaims: response.referenced_claims || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ **Processing Error**: ${err.message || 'Failed to process your request.'} Please verify backend connectivity.`,
          toolsCalled: [],
          referencedClaims: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSession = async () => {
    try {
      await resetChatSession(sessionId);
      setMessages([
        {
          role: 'assistant',
          content: 'Session memory cleared. What would you like to investigate next?',
          toolsCalled: [],
          referencedClaims: [],
        },
      ]);
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  const renderFormattedContent = (content) => {
    // Basic Markdown formatting helper for tables, bold, bullets, and claim badges
    const lines = content.split('\n');

    return (
      <div className="space-y-2 text-[13px] leading-relaxed">
        {lines.map((line, idx) => {
          const trimmed = line.trim();

          // Header line
          if (trimmed.startsWith('### ')) {
            return (
              <h4 key={idx} className="font-bold text-primary text-[14px] mt-2 mb-1 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">subdirectory_arrow_right</span>
                {trimmed.replace('### ', '')}
              </h4>
            );
          }
          if (trimmed.startsWith('**') && trimmed.endsWith(':**')) {
            return (
              <p key={idx} className="font-semibold text-on-surface mt-2">
                {trimmed.replace(/\*\*/g, '')}
              </p>
            );
          }

          // Bullet point
          if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            const bulletText = trimmed.substring(2);
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-primary mt-1 text-[8px]">●</span>
                <span className="flex-1">{formatInlineMarkup(bulletText)}</span>
              </div>
            );
          }

          // Empty line
          if (!trimmed) {
            return <div key={idx} className="h-1.5" />;
          }

          // Normal paragraph
          return <p key={idx}>{formatInlineMarkup(trimmed)}</p>;
        })}
      </div>
    );
  };

  const formatInlineMarkup = (text) => {
    // Replace **bold** and `code` with styled React fragments
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-on-surface">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        const codeVal = part.slice(1, -1);
        const isClaimId = codeVal.toUpperCase().startsWith('CLM');
        return (
          <span
            key={i}
            onClick={() => {
              if (isClaimId && onSelectClaim) {
                onSelectClaim(codeVal);
              }
            }}
            className={`font-code-num font-bold px-1.5 py-0.5 rounded text-[11px] mx-0.5 inline-block ${
              isClaimId
                ? 'bg-primary/15 text-primary border border-primary/30 cursor-pointer hover:bg-primary/25 transition-colors'
                : 'bg-surface-container text-on-surface-variant'
            }`}
            title={isClaimId ? `Click to inspect dossier for ${codeVal}` : undefined}
          >
            {codeVal}
            {isClaimId && <span className="material-symbols-outlined text-[10px] ml-1 align-middle">open_in_new</span>}
          </span>
        );
      }
      return part;
    });
  };

  const getToolBadge = (tool) => {
    switch (tool) {
      case 'query_claims_db':
        return { label: 'SQL Claims DB Query', icon: 'database', bg: 'bg-primary/10 text-primary border-primary/20' };
      case 'search_incident_precedents':
        return { label: 'ChromaDB Vector Match', icon: 'hub', bg: 'bg-secondary/15 text-secondary border-secondary/30' };
      case 'get_claim_dossier':
        return { label: '360° Dossier Inspection', icon: 'assignment', bg: 'bg-tertiary/15 text-tertiary border-tertiary/30' };
      case 'get_system_kpis':
        return { label: 'Portfolio Analytics Engine', icon: 'query_stats', bg: 'bg-primary-container text-on-primary-container border-outline/20' };
      default:
        return { label: tool, icon: 'bolt', bg: 'bg-surface-container text-on-surface-variant border-outline/20' };
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] mt-14 bg-background max-w-6xl mx-auto px-4 py-4">
      {/* Top Banner */}
      <div className="flex items-center justify-between bg-surface-container-low border border-outline-variant/30 rounded-2xl px-5 py-3.5 shadow-sm mb-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-container flex items-center justify-center shadow-sm">
            <span className="material-symbols-outlined text-primary text-[22px]">smart_toy</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-on-surface">Aegis AI Adjuster Copilot</h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary border border-primary/20 tracking-wider">
                UNIVERSAL RE-ACT AGENT
              </span>
            </div>
            <p className="text-[11px] text-on-surface-variant">
              Dynamic tool-equipped claims intelligence across 1,813 claims, ChromaDB narratives, and forensic ML models.
            </p>
          </div>
        </div>

        <button
          onClick={handleResetSession}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-outline-variant/40 bg-surface-container-lowest text-on-surface-variant hover:text-on-surface hover:bg-surface-container text-[12px] font-medium transition-colors"
          title="Clear conversation memory"
        >
          <span className="material-symbols-outlined text-[16px]">refresh</span>
          <span>Reset Thread</span>
        </button>
      </div>

      {/* Quick Suggestions Bar */}
      <div className="mb-3 shrink-0">
        <div className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <span className="material-symbols-outlined text-[14px] text-primary">lightbulb</span>
          Quick Inquiries for Adjusters
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1.5 scrollbar-thin">
          {suggestions.map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(item.prompt)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface-container-lowest border border-outline-variant/30 hover:border-primary/40 hover:bg-surface-container transition-all text-left shrink-0 group shadow-xs"
            >
              <span className="material-symbols-outlined text-[16px] text-primary group-hover:scale-110 transition-transform">
                {item.icon}
              </span>
              <div className="flex flex-col">
                <span className="text-[10px] font-bold text-on-surface-variant uppercase">{item.category}</span>
                <span className="text-[12px] text-on-surface max-w-[240px] truncate">{item.prompt}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Thread */}
      <div className="flex-1 overflow-y-auto bg-surface-container-lowest/60 border border-outline-variant/30 rounded-2xl p-4 sm:p-5 space-y-4 shadow-inner">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 max-w-4xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center shadow-xs text-white ${
                msg.role === 'user' ? 'bg-primary' : 'bg-surface-container-high border border-outline-variant/40 text-primary'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">
                {msg.role === 'user' ? 'person' : 'shield'}
              </span>
            </div>

            {/* Bubble */}
            <div
              className={`flex flex-col rounded-2xl p-4 shadow-xs max-w-[85%] sm:max-w-[80%] ${
                msg.role === 'user'
                  ? 'bg-primary-container text-on-primary-container border border-primary/20'
                  : 'bg-surface-container-low border border-outline-variant/40 text-on-surface'
              }`}
            >
              {/* Tool Execution Badges */}
              {msg.toolsCalled && msg.toolsCalled.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 mb-2.5 pb-2 border-b border-outline-variant/30">
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant mr-1">
                    Tools Executed:
                  </span>
                  {msg.toolsCalled.map((tool, tIdx) => {
                    const b = getToolBadge(tool);
                    return (
                      <span
                        key={tIdx}
                        className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold border ${b.bg}`}
                      >
                        <span className="material-symbols-outlined text-[12px]">{b.icon}</span>
                        {b.label}
                      </span>
                    );
                  })}
                </div>
              )}

              {/* Message Body */}
              <div className="overflow-x-auto">{renderFormattedContent(msg.content)}</div>

              {/* Referenced Claims Quick Links */}
              {msg.referencedClaims && msg.referencedClaims.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-outline-variant/30 flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant flex items-center gap-1">
                    <span className="material-symbols-outlined text-[13px]">link</span>
                    Cited Claims:
                  </span>
                  {msg.referencedClaims.map((cid, cIdx) => (
                    <button
                      key={cIdx}
                      onClick={() => onSelectClaim && onSelectClaim(cid)}
                      className="flex items-center gap-1 px-2 py-0.5 rounded bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 text-[11px] font-code-num font-bold transition-colors"
                      title={`Open Dossier for ${cid}`}
                    >
                      <span>{cid}</span>
                      <span className="material-symbols-outlined text-[11px]">arrow_forward</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Bubble */}
        {loading && (
          <div className="flex gap-3 max-w-xl">
            <div className="w-8 h-8 rounded-xl bg-surface-container-high border border-outline-variant/40 flex items-center justify-center text-primary shadow-xs">
              <span className="material-symbols-outlined text-[18px] animate-spin">refresh</span>
            </div>
            <div className="bg-surface-container-low border border-outline-variant/40 rounded-2xl p-4 shadow-xs">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                </span>
                <span className="text-[12px] text-on-surface-variant font-medium">
                  Reasoning over claims database &amp; invoking tools...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="mt-3 flex items-center gap-2 bg-surface-container-low border border-outline-variant/40 rounded-2xl p-2 shadow-sm focus-within:border-primary/60 transition-colors shrink-0"
      >
        <span className="material-symbols-outlined text-on-surface-variant ml-2 text-[20px]">
          chat_paste_go
        </span>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask anything... e.g. 'Show top high risk fire claims' or 'Why was CLM-01228 flagged?'"
          disabled={loading}
          className="flex-1 bg-transparent border-none outline-none text-[13px] text-on-surface placeholder:text-on-surface-variant/60 px-2"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || loading}
          className={`flex items-center justify-center w-10 h-10 rounded-xl transition-all shadow-xs ${
            inputText.trim() && !loading
              ? 'bg-primary text-on-primary hover:bg-primary/90'
              : 'bg-surface-container text-on-surface-variant/40 cursor-not-allowed'
          }`}
          title="Send inquiry"
        >
          <span className="material-symbols-outlined text-[18px]">send</span>
        </button>
      </form>
    </div>
  );
}

/**
 * Aegis Centralized API Client
 * Connects directly to FastAPI backend on port 8000
 */

const BASE_URL = ''; // Relative path for proxy or direct origin

export async function fetchStats() {
  const res = await fetch(`${BASE_URL}/api/stats`);
  if (!res.ok) throw new Error('Failed to load system stats');
  return res.json();
}

export async function fetchClaims({ page = 1, limit = 25, query = '', policyType = '', status = '' } = {}) {
  const params = new URLSearchParams({ page, limit });
  if (query) params.append('query', query);
  if (policyType && policyType !== 'ALL') params.append('policy_type', policyType);
  if (status && status !== 'ALL') params.append('status', status);

  const res = await fetch(`${BASE_URL}/api/claims?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch claims list');
  return res.json();
}

export async function fetchClaimDossier(claimId) {
  const res = await fetch(`${BASE_URL}/api/claims/${claimId}`);
  if (!res.ok) throw new Error(`Failed to load dossier for ${claimId}`);
  return res.json();
}

export async function runInvestigation(claimId) {
  const res = await fetch(`${BASE_URL}/api/investigate/${claimId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'LangGraph multi-agent investigation failed');
  }
  return res.json();
}

export async function submitAdjusterDecision({ claimId, decision, notes = '', adjusterName = 'Senior Adjuster' }) {
  const res = await fetch(`${BASE_URL}/api/adjuster/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      claim_id: claimId,
      decision,
      notes,
      adjuster_name: adjusterName,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to submit adjuster decision');
  }
  return res.json();
}

export async function searchSimilarClaims({ queryText, policyType = '', topK = 5 }) {
  const res = await fetch(`${BASE_URL}/api/search/similar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query_text: queryText,
      policy_type: policyType || null,
      top_k: topK,
    }),
  });
  if (!res.ok) throw new Error('Vector semantic search failed');
  return res.json();
}

export async function fetchIngestionLogs(limit = 100) {
  const res = await fetch(`${BASE_URL}/api/ingest/logs?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to load ingestion event logs');
  return res.json();
}

export async function fetchPipelineStatus() {
  const res = await fetch(`${BASE_URL}/api/ingest/status`);
  if (!res.ok) throw new Error('Failed to load pipeline health');
  return res.json();
}

export async function submitSingleClaim(claimPayload) {
  const res = await fetch(`${BASE_URL}/api/ingest/claim`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(claimPayload),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Claim ingestion failed');
  }
  return data;
}

export async function uploadBatchCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/api/ingest/csv`, {
    method: 'POST',
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Batch CSV ingestion failed');
  }
  return data;
}

export async function fetchBenchmarks() {
  const res = await fetch(`${BASE_URL}/api/evaluation/metrics`);
  if (!res.ok) throw new Error('Failed to load evaluation benchmarks');
  return res.json();
}

export async function sendChatMessage({ message, sessionId = 'default_adjuster' }) {
  const res = await fetch(`${BASE_URL}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Chat request failed');
  }
  return res.json();
}

export async function resetChatSession(sessionId = 'default_adjuster') {
  const res = await fetch(`${BASE_URL}/api/chat/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error('Failed to reset chat session');
  return res.json();
}

export async function fetchChatSuggestions() {
  const res = await fetch(`${BASE_URL}/api/chat/suggestions`);
  if (!res.ok) throw new Error('Failed to load chat suggestions');
  return res.json();
}

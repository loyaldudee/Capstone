import React, { useState, useEffect, useRef } from 'react';
import {
  fetchPipelineStatus,
  fetchIngestionLogs,
  submitSingleClaim,
  uploadBatchCsv,
} from '../api';

export default function KafkaStreamPortal({ onRefreshStats }) {
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [logPollingActive, setLogPollingActive] = useState(true);

  // Form State
  const [formData, setFormData] = useState({
    policy_type: 'Auto',
    customer_id: 'CUST_1001',
    claim_amount: '12500',
    incident_type: 'Collision',
    incident_severity: 'Moderate',
    reporting_delay_days: '2',
    police_report_filed: 'Yes',
    witness_present: 'Yes',
    incident_description: 'Vehicle collided with highway guardrail during heavy sleet.',
  });
  const [submittingClaim, setSubmittingClaim] = useState(false);
  const [formResponse, setFormResponse] = useState(null);
  const [formError, setFormError] = useState('');

  // CSV Batch Upload State
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadingCsv, setUploadingCsv] = useState(false);
  const [csvResult, setCsvResult] = useState(null);
  const [csvError, setCsvError] = useState('');

  const terminalEndRef = useRef(null);

  // Poll logs and pipeline status
  useEffect(() => {
    loadPipelineHealth();
    loadLogs();

    const interval = setInterval(() => {
      if (logPollingActive) {
        loadLogs();
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [logPollingActive]);

  const loadPipelineHealth = async () => {
    try {
      setLoadingStatus(true);
      const data = await fetchPipelineStatus();
      setPipelineStatus(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingStatus(false);
    }
  };

  const loadLogs = async () => {
    try {
      const data = await fetchIngestionLogs(100);
      setLogs(data.logs || []);
    } catch (err) {
      console.error(err);
    }
  };

  // Submit manual claim
  const handleClaimSubmit = async (e) => {
    e.preventDefault();
    setSubmittingClaim(true);
    setFormError('');
    setFormResponse(null);

    try {
      const payload = {
        policy_type: formData.policy_type,
        customer_id: formData.customer_id,
        claim_amount: parseFloat(formData.claim_amount) || 0,
        incident_type: formData.incident_type,
        incident_severity: formData.incident_severity,
        reporting_delay_days: parseInt(formData.reporting_delay_days) || 0,
        police_report_filed: formData.police_report_filed,
        witness_present: formData.witness_present,
        incident_description: formData.incident_description,
      };

      const res = await submitSingleClaim(payload);
      setFormResponse(res);
      loadLogs();
      loadPipelineHealth();
      onRefreshStats();
    } catch (err) {
      setFormError(err.message || 'Claim ingestion failed');
    } finally {
      setSubmittingClaim(false);
    }
  };

  // Upload Batch CSV
  const handleCsvUpload = async () => {
    if (!selectedFile) return;
    setUploadingCsv(true);
    setCsvError('');
    setCsvResult(null);

    try {
      const res = await uploadBatchCsv(selectedFile);
      setCsvResult(res);
      setSelectedFile(null);
      loadLogs();
      loadPipelineHealth();
      onRefreshStats();
    } catch (err) {
      setCsvError(err.message || 'Batch CSV upload failed');
    } finally {
      setUploadingCsv(false);
    }
  };

  const getLogBadge = (status) => {
    switch (status) {
      case 'SUCCESS':
        return 'text-[#10b981] bg-[#10b981]/15';
      case 'ERROR':
        return 'text-error bg-error/15 font-bold';
      case 'WARNING':
        return 'text-tertiary bg-tertiary/15 font-bold';
      case 'INFO':
      default:
        return 'text-primary bg-primary/15';
    }
  };

  return (
    <div className="flex flex-col gap-space-lg">
      {/* Top Header & Operational Badges */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md">
        <div className="flex flex-col gap-space-xs">
          <div className="flex items-center gap-space-xs">
            <span className="inline-flex items-center gap-1.5 px-space-xs py-[2px] rounded-full bg-primary/10 text-primary font-label-sm text-xs font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
              INGEST-CORE // V4.2 • Real-Time Intake Runtime
            </span>
            <span className="inline-flex items-center px-space-xs py-[2px] rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-xs font-semibold">
              TOPIC: raw-claims-ingest
            </span>
          </div>
          <h1 className="font-headline-lg text-2xl lg:text-3xl text-on-surface font-bold tracking-tight">
            Kafka Ingestion &amp; Stream Portal
          </h1>
          <p className="font-body-md text-xs text-on-surface-variant max-w-3xl">
            High-throughput asynchronous telemetry intake, deterministic data sanitization, and vectorized persistence layer.
          </p>
        </div>

        {/* Right Header Buttons */}
        <div className="flex items-center gap-space-sm self-start lg:self-center">
          <button
            onClick={() => setLogs([])}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-tertiary-fixed text-on-tertiary-container hover:bg-tertiary-container transition-colors shadow-xs font-label-md text-xs font-semibold"
          >
            <span className="material-symbols-outlined text-[16px] text-tertiary">delete_sweep</span>
            <span>Clear Terminal</span>
          </button>
          <button
            onClick={() => {
              loadPipelineHealth();
              loadLogs();
            }}
            disabled={loadingStatus}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-primary-container text-on-primary-container hover:bg-primary-fixed-dim transition-colors shadow-xs font-label-md text-xs font-semibold"
          >
            <span className="material-symbols-outlined text-[16px]">sync</span>
            <span>Refresh Telemetry</span>
          </button>
        </div>
      </div>

      {/* Telemetry Status Ribbon */}
      <div className="w-full bg-surface-container-lowest shadow-xs rounded-xl px-space-md py-space-xs flex flex-wrap items-center justify-between gap-space-sm font-label-sm text-xs text-on-surface-variant border border-outline-variant/30">
        <div className="flex items-center gap-space-md flex-wrap">
          <span className="flex items-center gap-1 font-semibold text-on-surface">
            <span className="material-symbols-outlined text-[15px] text-primary">dns</span>
            Node: <span className="font-code-num text-primary">AEGIS-KFK-09</span>
          </span>
          <span className="text-outline-variant">•</span>
          <span>CLUSTER-ID: <strong className="text-on-surface font-code-num">EU-CENTRAL-01</strong></span>
          <span className="text-outline-variant">•</span>
          <span>Time-Sync: <span className="text-primary font-medium">UTC+00.00 [PTP LOCKED]</span></span>
        </div>
        <div className="flex items-center gap-space-sm">
          <span className="inline-flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span>
            Heartbeat: <strong className="text-on-surface font-code-num">0.4s</strong>
          </span>
          <span className="px-2 py-0.5 rounded bg-surface-container font-code-num text-on-surface-variant text-[11px]">
            PAR-LEADER: 0
          </span>
        </div>
      </div>

      {/* 4 Telemetry Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md">
        {/* Card 1: Broker Status */}
        <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col justify-between relative overflow-hidden">
          <div
            className={`h-1 absolute top-0 left-0 right-0 ${
              pipelineStatus?.kafka_connected ? 'bg-[#10b981]' : 'bg-[#f59e0b]'
            }`}
          />
          <div className="flex items-center justify-between mb-space-xs">
            <span className="font-label-sm text-xs uppercase font-semibold text-on-surface-variant">
              Broker Status
            </span>
            <span
              className={`w-2 h-2 rounded-full ${
                pipelineStatus?.kafka_connected ? 'bg-[#10b981] animate-pulse' : 'bg-[#f59e0b]'
              }`}
            />
          </div>
          <div>
            <span className="font-title-md text-base font-bold text-on-surface">
              {pipelineStatus?.kafka_connected ? 'Kafka Connected (Live)' : 'Direct Pipeline (Standby)'}
            </span>
            <div className="text-[11px] text-on-surface-variant mt-1">
              Broker Port: 9092 • {pipelineStatus?.kafka_connected ? 'Streaming active' : 'Fallback active'}
            </div>
          </div>
        </div>

        {/* Card 2: Ingest Topic */}
        <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col justify-between relative overflow-hidden">
          <div className="h-1 absolute top-0 left-0 right-0 bg-primary-container" />
          <div className="flex items-center justify-between mb-space-xs">
            <span className="font-label-sm text-xs uppercase font-semibold text-on-surface-variant">
              Ingest Topic
            </span>
            <span className="material-symbols-outlined text-[18px] text-primary">topic</span>
          </div>
          <div>
            <span className="font-title-md text-base font-bold text-on-surface">
              raw-claims-ingest
            </span>
            <div className="text-[11px] text-on-surface-variant mt-1">
              Partitions: 1 • Replication: 1
            </div>
          </div>
        </div>

        {/* Card 3: Events Logged */}
        <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col justify-between relative overflow-hidden">
          <div className="h-1 absolute top-0 left-0 right-0 bg-secondary-container" />
          <div className="flex items-center justify-between mb-space-xs">
            <span className="font-label-sm text-xs uppercase font-semibold text-on-surface-variant">
              Telemetry Buffer
            </span>
            <span className="material-symbols-outlined text-[18px] text-secondary">database</span>
          </div>
          <div>
            <span className="font-title-md text-base font-bold text-on-surface">
              {logs.length} Events Buffered
            </span>
            <div className="text-[11px] text-on-surface-variant mt-1">
              In-memory circular FIFO (Cap: 200)
            </div>
          </div>
        </div>

        {/* Card 4: Consumer Thread */}
        <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col justify-between relative overflow-hidden">
          <div className="h-1 absolute top-0 left-0 right-0 bg-tertiary-fixed" />
          <div className="flex items-center justify-between mb-space-xs">
            <span className="font-label-sm text-xs uppercase font-semibold text-on-surface-variant">
              Consumer Worker
            </span>
            <span className="material-symbols-outlined text-[18px] text-tertiary">alt_route</span>
          </div>
          <div>
            <span className="font-title-md text-base font-bold text-on-surface">
              {pipelineStatus?.consumer_active ? 'Active Polling' : 'Consumer Daemon'}
            </span>
            <div className="text-[11px] text-on-surface-variant mt-1">
              Sanitizer $\rightarrow$ RDBMS $\rightarrow$ ChromaDB
            </div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Deck: Left Form, Right CSV & Terminal */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-space-lg">
        {/* Left Column: Manual Claim Ingestion Form */}
        <div className="xl:col-span-5 bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col gap-space-sm">
          <div className="flex items-center gap-2 pb-2 border-b border-outline-variant/20">
            <span className="material-symbols-outlined text-primary text-[20px]">post_add</span>
            <div>
              <h2 className="font-headline-sm text-sm font-bold text-on-surface">
                Manual Claim Intake &amp; Sanitation Gateway
              </h2>
              <span className="text-[11px] text-on-surface-variant">
                Direct client intake with instant data sanitization
              </span>
            </div>
          </div>

          {formError && (
            <div className="p-3 rounded-xl bg-error-container text-on-error-container text-xs border border-error/20 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">error</span>
              <span>{formError}</span>
            </div>
          )}

          {formResponse && (
            <div className="p-3 rounded-xl bg-[#B2EAD3]/40 text-[#154B35] text-xs border border-[#B2EAD3] flex flex-col gap-1">
              <div className="flex items-center gap-1 font-bold">
                <span className="material-symbols-outlined text-[18px]">check_circle</span>
                <span>Claim Ingested Successfully!</span>
              </div>
              <span className="text-[11px] opacity-90">{formResponse.message}</span>
            </div>
          )}

          <form onSubmit={handleClaimSubmit} className="flex flex-col gap-3 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="font-semibold text-on-surface-variant block mb-1">
                  Policy Line
                </label>
                <select
                  value={formData.policy_type}
                  onChange={(e) => setFormData({ ...formData, policy_type: e.target.value })}
                  className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface font-semibold focus:outline-none focus:border-primary"
                >
                  <option value="Auto">Auto</option>
                  <option value="Fire_Property">Fire / Property</option>
                  <option value="Boat_Marine">Boat / Marine</option>
                  <option value="Life_Health">Life / Health</option>
                  <option value="Accident_Liability">Accident / Liability</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-on-surface-variant block mb-1">
                  Customer / Policyholder ID
                </label>
                <input
                  type="text"
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  placeholder="e.g. CUST_1001"
                  className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="font-semibold text-on-surface-variant block mb-1">
                  Claim Amount (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.claim_amount}
                  onChange={(e) => setFormData({ ...formData, claim_amount: e.target.value })}
                  placeholder="e.g. 12500"
                  className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface font-code-num focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="font-semibold text-on-surface-variant block mb-1">
                  Incident Severity
                </label>
                <select
                  value={formData.incident_severity}
                  onChange={(e) => setFormData({ ...formData, incident_severity: e.target.value })}
                  className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface font-semibold focus:outline-none focus:border-primary"
                >
                  <option value="Minor">Minor</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Severe">Severe</option>
                  <option value="Catastrophic">Catastrophic</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="font-semibold text-on-surface-variant block mb-1">
                  Incident Type
                </label>
                <select
                  value={formData.incident_type}
                  onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
                  className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface font-semibold focus:outline-none focus:border-primary"
                >
                  <option value="Collision">Collision</option>
                  <option value="Theft">Theft</option>
                  <option value="Water Damage">Water Damage</option>
                  <option value="Fire">Fire</option>
                  <option value="Vandalism">Vandalism</option>
                  <option value="Medical Emergency">Medical Emergency</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-on-surface-variant block mb-1">
                  Reporting Delay (Days)
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.reporting_delay_days}
                  onChange={(e) => setFormData({ ...formData, reporting_delay_days: e.target.value })}
                  className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface font-code-num focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <label className="flex items-center gap-2 p-2 rounded-lg bg-surface-container-low border border-outline-variant/20 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.police_report_filed === 'Yes'}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      police_report_filed: e.target.checked ? 'Yes' : 'No',
                    })
                  }
                  className="rounded text-primary focus:ring-primary"
                />
                <span className="text-on-surface font-medium">Police Report Filed</span>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg bg-surface-container-low border border-outline-variant/20 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.witness_present === 'Yes'}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      witness_present: e.target.checked ? 'Yes' : 'No',
                    })
                  }
                  className="rounded text-primary focus:ring-primary"
                />
                <span className="text-on-surface font-medium">Witness Present</span>
              </label>
            </div>

            <div>
              <label className="font-semibold text-on-surface-variant block mb-1">
                Incident Narrative / Description
              </label>
              <textarea
                rows={3}
                value={formData.incident_description}
                onChange={(e) => setFormData({ ...formData, incident_description: e.target.value })}
                placeholder="Detailed description of incident for semantic vector store..."
                className="w-full p-2 rounded-lg bg-surface-container-low border border-outline-variant/40 text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <button
              type="submit"
              disabled={submittingClaim}
              className="w-full py-2.5 px-4 rounded-xl bg-primary text-on-primary font-bold text-xs flex items-center justify-center gap-2 shadow-xs hover:bg-primary/90 transition-all disabled:opacity-50"
            >
              {submittingClaim ? (
                <>
                  <span className="material-symbols-outlined text-[18px] animate-spin">
                    progress_activity
                  </span>
                  <span>Publishing Event to Kafka...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">publish</span>
                  <span>Sanitize &amp; Stream Claim to Kafka</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: CSV Batch Upload + Live Terminal */}
        <div className="xl:col-span-7 flex flex-col gap-space-md">
          {/* CSV Batch Upload Card */}
          <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col gap-space-xs">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">upload_file</span>
                <h3 className="font-headline-sm text-sm font-bold text-on-surface">
                  Batch Claims CSV Streaming Upload
                </h3>
              </div>
              <span className="text-[11px] text-on-surface-variant font-medium">
                Try <code>sample_clean_claims.csv</code> or <code>sample_dirty_claims.csv</code>
              </span>
            </div>

            {csvError && (
              <div className="p-3 rounded-xl bg-error-container text-on-error-container text-xs border border-error/20 flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">error</span>
                <span>{csvError}</span>
              </div>
            )}

            {csvResult && (
              <div className="p-3 rounded-xl bg-[#B2EAD3]/40 text-[#154B35] text-xs border border-[#B2EAD3] flex flex-col gap-1">
                <div className="flex items-center gap-1 font-bold">
                  <span className="material-symbols-outlined text-[18px]">check_circle</span>
                  <span>Batch Ingestion Completed!</span>
                </div>
                <span className="text-[11px]">
                  Uploaded <strong>{csvResult.filename}</strong>: {csvResult.total_records_ingested} records streamed into Kafka topic.
                </span>
              </div>
            )}

            <div className="flex items-center gap-2 pt-1">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                className="flex-1 text-xs text-on-surface-variant file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-primary-container file:text-on-primary-container hover:file:opacity-90 cursor-pointer"
              />
              <button
                onClick={handleCsvUpload}
                disabled={!selectedFile || uploadingCsv}
                className="py-2 px-4 rounded-xl bg-on-surface text-surface font-bold text-xs hover:opacity-90 transition-opacity disabled:opacity-40 flex items-center gap-1.5"
              >
                {uploadingCsv ? (
                  <>
                    <span className="material-symbols-outlined text-[16px] animate-spin">
                      progress_activity
                    </span>
                    <span>Streaming...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[16px]">cloud_upload</span>
                    <span>Upload &amp; Stream Batch</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Live Terminal Log Stream Monitor */}
          <div className="bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-outline-variant/30 flex flex-col gap-2 flex-1">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
                <span className="font-headline-sm text-sm font-bold text-on-surface">
                  Live Kafka &amp; Sanitation Event Stream Monitor
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setLogPollingActive(!logPollingActive)}
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    logPollingActive ? 'bg-[#B2EAD3]/40 text-[#154B35]' : 'bg-surface-container text-on-surface-variant'
                  }`}
                >
                  {logPollingActive ? 'LIVE STREAMING' : 'PAUSED'}
                </button>
                <span className="text-[11px] font-code-num text-on-surface-variant">
                  {logs.length} events
                </span>
              </div>
            </div>

            {/* Terminal Window */}
            <div className="h-[360px] bg-[#111c2c] text-[#ebf1ff] p-3 rounded-xl overflow-y-auto font-code-num text-[11px] flex flex-col gap-1.5 shadow-inner">
              {logs.length === 0 ? (
                <div className="text-center text-outline-variant my-auto italic">
                  Awaiting ingestion events... Ingest a claim or upload a CSV to see live Kafka telemetry.
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="flex items-start gap-2 leading-tight">
                    <span className="text-outline-variant opacity-80 shrink-0">
                      {log.timestamp ? log.timestamp.split(' ')[1] : '--:--:--'}
                    </span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-bold shrink-0 ${getLogBadge(
                        log.status
                      )}`}
                    >
                      {log.status}
                    </span>
                    <span className="text-primary-fixed-dim font-bold shrink-0">
                      [{log.stage}]
                    </span>
                    <span className="text-tertiary-fixed font-semibold shrink-0">
                      {log.claim_id}:
                    </span>
                    <span className="text-surface-bright break-all">
                      {log.message}
                    </span>
                  </div>
                ))
              )}
              <div ref={terminalEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

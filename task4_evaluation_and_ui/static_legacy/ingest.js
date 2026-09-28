/* Aegis Kafka Ingestion Portal - Interactive JavaScript */
document.addEventListener("DOMContentLoaded", () => {
  fetchPipelineStatus();
  fetchStreamingLogs();
  fetchRecentIngestedClaims();
  setInterval(fetchPipelineStatus, 8000);
  setInterval(fetchStreamingLogs, 3000);
  setInterval(fetchRecentIngestedClaims, 5000);


  // Single Claim Form Handler
  const form = document.getElementById("single-claim-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.innerText = "⏳ Sanitizing & Publishing to Kafka...";

    // Build payload from form fields
    const payload = {
      policy_type: document.getElementById("policy_type").value,
      claim_amount: parseFloat(document.getElementById("claim_amount").value.replace(/[^0-9.-]/g, '')) || 0,
      incident_type: document.getElementById("incident_type").value,
      incident_severity: document.getElementById("incident_severity").value,
      reporting_delay_days: parseInt(document.getElementById("reporting_delay_days").value, 10) || 0,
      prior_claims_count: parseInt(document.getElementById("prior_claims_count").value, 10) || 0,
      police_report_filed: document.getElementById("police_report_filed").value,
      witness_present: document.getElementById("witness_present").value,
      incident_description: document.getElementById("incident_description").value
    };

    console.log("[Aegis Ingest] Submitting payload:", JSON.stringify(payload, null, 2));

    try {
      const res = await fetch("/api/ingest/claim", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      console.log("[Aegis Ingest] Response status:", res.status);

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        throw new Error(errData.detail || `Server returned ${res.status}`);
      }

      const data = await res.json();
      console.log("[Aegis Ingest] Response data:", JSON.stringify(data, null, 2));

      const box = document.getElementById("submit-response-box");
      box.style.display = "block";

      if (data.published_to_kafka) {
        // Kafka path — show queued confirmation
        box.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <h4 style="font-size: 0.9rem; color: var(--accent-cyan); font-weight:bold;">✅ Claim Published to Kafka Successfully!</h4>
            <span style="background: rgba(16,185,129,0.2); color: #10b981; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: bold;">🟢 Streamed Live to Kafka Topic 'raw-claims-ingest'</span>
          </div>
          <div style="font-size: 0.85rem; color: #e5e7eb; margin-bottom: 0.75rem;">
            <strong>Policy:</strong> ${data.cleaned_data.policy_type} | 
            <strong>Amount:</strong> €${Number(data.cleaned_data.claim_amount).toLocaleString()} | 
            <strong>Status:</strong> <span style="color: var(--accent-cyan);">${data.cleaned_data.status || 'Queued for processing'}</span>
          </div>
          <div style="font-size: 0.8rem; color: #9ca3af; padding: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 6px;">
            ℹ️ The Kafka consumer is processing this claim in the background. It will appear in the claims table below within a few seconds.
          </div>
          <pre style="font-size: 0.75rem; font-family: monospace; color: #9ca3af; background: rgba(0,0,0,0.4); padding: 0.75rem; border-radius: 6px; overflow-x: auto; margin-top: 0.5rem;">${JSON.stringify(data, null, 2)}</pre>
        `;
      } else {
        // Fallback direct path
        box.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <h4 style="font-size: 0.9rem; color: var(--accent-cyan); font-weight:bold;">✅ Claim ${data.cleaned_data.claim_id} Ingested & Sanitized!</h4>
            <span style="background: rgba(245,158,11,0.2); color: #f59e0b; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: bold;">🟠 Direct Pipeline Ingestion (Kafka Standby)</span>
          </div>
          <div style="font-size: 0.85rem; color: #e5e7eb; margin-bottom: 0.75rem;">
            <strong>Policy:</strong> ${data.cleaned_data.policy_type} | 
            <strong>Amount:</strong> €${Number(data.cleaned_data.claim_amount).toLocaleString()} | 
            <strong>Narrative:</strong> "${data.cleaned_data.incident_description}"
          </div>
          <pre style="font-size: 0.75rem; font-family: monospace; color: #9ca3af; background: rgba(0,0,0,0.4); padding: 0.75rem; border-radius: 6px; overflow-x: auto;">${JSON.stringify(data.cleaned_data, null, 2)}</pre>
        `;
      }

      // Refresh all panels after submission
      setTimeout(() => {
        fetchStreamingLogs();
        fetchPipelineStatus();
        fetchRecentIngestedClaims();
      }, 1500);

      // Refresh again after a bit for Kafka consumer to process
      setTimeout(() => fetchRecentIngestedClaims(), 5000);

      // Auto-scroll response box into view
      box.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (err) {
      console.error("[Aegis Ingest] Submission error:", err);
      const box = document.getElementById("submit-response-box");
      box.style.display = "block";
      box.innerHTML = `
        <div style="background: rgba(239,68,68,0.1); border: 1px solid #ef4444; padding: 1rem; border-radius: 8px;">
          <h4 style="color: #ef4444; margin-bottom: 0.5rem;">❌ Ingestion Failed</h4>
          <p style="color: #fca5a5; font-size: 0.85rem;">${err.message}</p>
          <p style="color: #9ca3af; font-size: 0.8rem; margin-top: 0.5rem;">Check the browser console (F12) and server logs for details.</p>
        </div>
      `;
    } finally {
      btn.disabled = false;
      btn.innerText = "🚀 Sanitize & Stream to Kafka";
    }
  });



  // Bulk CSV Upload Handler
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("csv-file-input");

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--accent-cyan)";
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "var(--panel-border)";
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--panel-border)";
    if (e.dataTransfer.files.length > 0) {
      handleCsvUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleCsvUpload(fileInput.files[0]);
    }
  });
});

async function fetchPipelineStatus() {
  try {
    const res = await fetch("/api/ingest/status");
    const data = await res.json();

    const dot = document.getElementById("kafka-dot");
    const text = document.getElementById("kafka-status-text");
    const desc = document.getElementById("status-mode-desc");

    if (data.kafka_connected) {
      dot.className = "dot green";
      text.innerText = "Kafka Connected (Live)";
      const consumerStatus = data.consumer_active ? " | Consumer: Active ✓" : " | Consumer: Idle";
      desc.innerText = `Active Broker at ${data.bootstrap_servers}. Streaming records to topic '${data.topic}'.${consumerStatus}`;
    } else {
      dot.className = "dot amber";
      text.innerText = "Direct Pipeline (Kafka Standby)";
      desc.innerText = `Kafka broker on port 9092 offline/standby. Operating in resilient Direct Ingestion mode.`;
    }
  } catch (err) {
    console.error("Failed to fetch pipeline status:", err);
  }
}

async function fetchStreamingLogs() {
  try {
    const res = await fetch("/api/ingest/logs?limit=30");
    const data = await res.json();
    const terminal = document.getElementById("terminal-window");

    if (!data.logs || data.logs.length === 0) return;

    terminal.innerHTML = "";
    data.logs.forEach(log => {
      const entry = document.createElement("div");
      entry.className = "log-entry";
      
      // Color-code by status
      let statusClass = log.status || "INFO";
      let statusColor = "#9ca3af";
      if (statusClass === "SUCCESS") statusColor = "#10b981";
      else if (statusClass === "WARNING") statusColor = "#f59e0b";
      else if (statusClass === "ERROR") statusColor = "#ef4444";
      else if (statusClass === "INFO") statusColor = "#60a5fa";

      entry.innerHTML = `
        <span class="log-time">[${log.timestamp ? log.timestamp.split(" ")[1] : "---"}]</span>
        <span class="log-stage" style="color: ${statusColor};">[${log.stage}]</span>
        <span class="log-id">${log.claim_id}:</span>
        <span class="log-msg" style="color: ${statusColor};">${log.message}</span>
      `;
      terminal.appendChild(entry);
    });

    terminal.scrollTop = terminal.scrollHeight;
  } catch (err) {
    console.error("Failed to fetch logs:", err);
  }
}

async function fetchRecentIngestedClaims() {
  try {
    const res = await fetch("/api/claims?page=1&limit=8");
    const data = await res.json();
    const tbody = document.getElementById("ingested-claims-table-body");
    if (!tbody || !data.claims) return;

    tbody.innerHTML = "";
    if (data.claims.length === 0) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td colspan="6" style="padding: 1rem; text-align: center; color: var(--text-muted);">No claims found in database.</td>`;
      tbody.appendChild(tr);
      return;
    }

    data.claims.forEach(c => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid var(--panel-border)";
      
      const badgeStyle = c.claim_id.startsWith("CLM-INGEST") 
        ? "background: rgba(0, 242, 254, 0.15); color: var(--accent-cyan); font-weight: bold; padding: 0.15rem 0.5rem; border-radius: 4px;"
        : "color: var(--text-main); font-weight: 500;";

      tr.innerHTML = `
        <td style="padding: 0.75rem;"><span style="${badgeStyle}">${c.claim_id}</span></td>
        <td style="padding: 0.75rem;">${c.policy_type}</td>
        <td style="padding: 0.75rem; font-weight: bold;">€${Number(c.claim_amount).toLocaleString()}</td>
        <td style="padding: 0.75rem;"><span style="color: var(--accent-amber);">${c.incident_severity}</span></td>
        <td style="padding: 0.75rem; color: #d1d5db; max-width: 380px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">"${c.incident_description}"</td>
        <td style="padding: 0.75rem;"><span style="background: rgba(255,255,255,0.05); padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">${c.claim_status}</span></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to fetch recent ingested claims:", err);
  }
}


async function handleCsvUpload(file) {
  const statusDiv = document.getElementById("csv-upload-status");
  statusDiv.innerText = `⏳ Uploading and streaming '${file.name}'...`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/ingest/csv", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (res.ok) {
      statusDiv.innerHTML = `✅ <strong>${data.total_records_ingested}</strong> claims successfully ingested from <em>${data.filename}</em>! (Mode: ${data.mode || 'Unknown'})`;
      fetchStreamingLogs();
      setTimeout(() => fetchRecentIngestedClaims(), 3000);
    } else {
      statusDiv.innerText = `❌ Ingestion error: ${data.detail || "Upload failed."}`;
    }
  } catch (err) {
    statusDiv.innerText = `❌ Upload failed: ${err.message}`;
  }
}

# Aegis User Guide, Execution Manual & Feature Specification

## 1. Overview & System Purpose

**Aegis** is an enterprise-grade AI-powered Insurance Claims Intelligence, Fraud Detection, and Adjudication Decision Support Platform. Grounded in the real-world **COIL 2000 Insurance Benchmark** (9,822 customer demographic profiles and 86 socio-economic attributes), Aegis combines:

- **Predictive Machine Learning**: Supervised Random Forest risk scoring (ROC-AUC 0.9467) + Unsupervised Isolation Forest anomaly detection (90.24% specificity).
- **Dense Vector Search**: ChromaDB semantic indexing with `all-MiniLM-L6-v2` across 1,800+ claims narratives.
- **Stateful 6-Agent LangGraph Orchestration**: Concurrent parallel fan-out, fan-in LLM synthesis (`gpt-5-nano`), dynamic Agent-to-Agent (A2A) handoff to Special Investigation Units (SIU), and senior adjudication advisor directives.
- **Universal Agentic Chatbot Copilot**: Multi-turn natural language conversation with 4 deterministic tools for real-time querying, vector retrieval, and portfolio KPI analytics.
- **Event-Driven Streaming Ingestion**: High-throughput Apache Kafka pipeline with automated data sanitization and schema repair.
- **Human-in-the-Loop Governance**: Regulatory "Four-Eyes Principle" compliance with human adjuster adjudication gates.

---

## 2. Complete Project Feature Inventory

| Module / Area | Feature | Technical Implementation | Business / Operational Value |
| :--- | :--- | :--- | :--- |
| **Data Engine (Task 1)** | **COIL 2000 Demographic Grounding** | `task1_data_preparation/prepare_data.py` | 9,822 real-world profiles mapped to realistic multi-line policy claims with zero data leakage. |
| | **Temporal Zero-Leakage Windowing** | `cumcount()` chronological calculation | Eliminates lookahead bias by calculating prior claims relative to incident date. |
| | **Data Quality Sanitizer** | `task1_data_preparation/data_sanitizer.py` | Automatically repairs malformed values, handles outliers, and validates policy constraints. |
| | **Kafka Streaming Ingestion** | `kafka_service.py` & `streaming_worker.py` | Publishes incoming claims to `raw-claims-ingest` topic with async DB & vector persistence. |
| **Analytics & Search (Task 2)** | **Supervised Risk Classifier** | `task2_models_analytics/train_models.py` | Random Forest trained on 14 tabular features achieving 87.5% accuracy and 0.9467 ROC-AUC. |
| | **Unsupervised Anomaly Detector** | Isolation Forest + IQR Baselines | Detects multi-variate statistical anomalies and payout discrepancies without supervision. |
| | **Dense Semantic Vector Store** | ChromaDB + `all-MiniLM-L6-v2` | Instant semantic similarity retrieval across 1,800+ incident narratives and police reports. |
| **Multi-Agent Core (Task 3)** | **Parallel Fan-Out Retrieval & Risk** | LangGraph `StateGraph` | Concurrently invokes Retrieval, Risk Analysis, and Anomaly Detection agents for low latency. |
| | **Live LLM Executive Synthesis** | `gpt-5-nano` via `llm_client.py` | Generates factual, concise executive summaries grounding all specialist findings. |
| | **Dynamic A2A SIU Handoff** | Conditional Edge Router | Automatically transfers high-risk (`>= 70%`) or coverage-mismatched claims to Agent 5 (SIU). |
| | **Senior Adjudication Advisor** | `advisor_agent.py` | Formulates strategic claimant inquiry questions and fast-track adjudication directives. |
| **Chatbot Copilot** | **Universal Agentic Chat Engine** | `chatbot_engine.py` & `chat_routes.py` | Answers complex natural language adjuster queries using 4 parameterized tools. |
| | **Portfolio KPI Analytics Tool** | `tool_get_system_kpis` | Computes live approval rates, SIU escalation percentages, and portfolio distributions. |
| **UI & Adjudication (Task 4)** | **Claims Explorer & Live Dossier** | FastAPI HTML5/JS & React/Vite UI | Search, filter by risk tier/status, view 360° customer profile, and inspect timeline. |
| | **Human Adjudication Gate** | Four-Eyes Principle Sign-off | Allows adjusters to Approve, Reject, or Escalate claims with audit notes. |
| | **Automated Evaluation Benchmark** | `task4_evaluation_and_ui/evaluate_system.py` | Validates vector retrieval, ML models, factual grounding, and intent accuracy. |

---

## 3. Environment Prerequisites & Setup

### 3.1 Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12 installed.
- **Node.js**: Version 18+ and `npm` (if compiling the React frontend).
- **Git**: Installed and available in PATH.
- **Docker & Docker Compose** (Optional: for running PostgreSQL and Apache Kafka services).

### 3.2 Repository Directory Layout
```
Capstone/
├── main.py                         # FastAPI microservice entry point & lifespan
├── routes.py                       # Core claims, investigation & search REST endpoints
├── ingestion_routes.py             # Kafka streaming & CSV bulk upload REST endpoints
├── chat_routes.py                  # Adjuster AI Copilot Chatbot REST endpoints
├── chatbot_engine.py               # Universal 4-tool conversational LLM engine
├── database.py                     # SQLAlchemy engine, session maker & auto-seeding
├── models.py                       # Relational database models (Customers, Claims, etc.)
├── schemas.py                      # Pydantic v2 data transfer schemas (DTOs)
├── server.py                       # CLI execution runner alias
├── docker-compose.yml              # PostgreSQL + pgAdmin service configurations
├── requirements.txt                # Python dependencies
├── .env                            # API keys, database URLs, and configuration
├── task1_data_preparation/         # Data engineering, COIL 2000 & Kafka workers
├── task2_models_analytics/         # Scikit-learn models & ChromaDB vector store
├── task3_multi_agent_system/       # LangGraph 6-Agent forensic investigation core
├── task4_evaluation_and_ui/        # Evaluation suite, API tests, and Web UI static build
├── task5_documentation/            # Complete architecture, guides & documentation
└── frontend/                       # React / Vite / Tailwind UI source files
```

---

## 4. Step-by-Step Installation & Execution Guide

### Step 1: Virtual Environment Setup
Open a terminal in the project root:

```bash
# Windows (PowerShell / Command Prompt)
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies include `fastapi`, `uvicorn`, `langgraph`, `langchain-core`, `chromadb`, `sentence-transformers`, `scikit-learn`, `sqlalchemy`, `pydantic`, `openai`, `kafka-python`, `pandas`, `numpy`, `python-dotenv`)*.

### Step 3: Configure Environment Variables (`.env`)
Ensure a `.env` file exists in the project root with the following configuration:

```env
# LLM Provider Configuration
OPENAI_API_KEY=your_openai_or_custom_key_here
OPENAI_BASE_URL=https://api.aicredits.in/v1
MODEL_NAME=gpt-5-nano

# Relational Database Configuration
# Local SQLite default:
DATABASE_URL=sqlite:///./insurance.db
# Or Production PostgreSQL:
# DATABASE_URL=postgresql://aegis_user:aegis_secure_password_2026@localhost:5432/aegis_insurance

# Apache Kafka Broker Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

---

### Step 4: Prepare Data & Train Models (If rebuilding from scratch)
The repository includes pre-built databases and models. To retrain or re-seed from scratch:

```bash
# 1. Synthesize 9,822 COIL profiles and 1,800 grounded claims
python task1_data_preparation/prepare_data.py

# 2. Train Random Forest Classifier and Isolation Forest Anomaly Detector
python task2_models_analytics/train_models.py

# 3. Build ChromaDB Vector Store embeddings (1,800 incident narratives)
python task2_models_analytics/build_vector_store.py
```

---

### Step 5: Start the Backend Microservice
Run the FastAPI application server:

```bash
# Option A: Using the runner script
python server.py

# Option B: Direct Uvicorn invocation
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

When started, the server will output:
```
[Aegis Startup] Verifying database schema and auto-seeding...
[Aegis Startup] Pre-warming ChromaDB vector retrieval engine...
[Aegis Startup] ChromaDB vector engine ready.
[Aegis Startup] Starting Kafka consumer worker thread...
=================================================================
  AEGIS INSURANCE CLAIMS INTELLIGENCE ASSISTANT (MICROSERVICE)
  Running locally on http://127.0.0.1:8000
=================================================================
```

### Step 6: Access the Web Applications & Interactive Portals
Open your browser to:
- 🌐 **Main Claims Dashboard & Live Dossier**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 🔍 **ChromaDB Semantic Vector Search**: [http://127.0.0.1:8000/search](http://127.0.0.1:8000/search)
- 📥 **Kafka Ingestion & Data Sanitation Portal**: [http://127.0.0.1:8000/ingest](http://127.0.0.1:8000/ingest)
- 💬 **Adjuster AI Copilot Chatbot**: [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)
- 📖 **Interactive Swagger / OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **Redoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### Step 7: (Optional) Running the React / Vite Frontend in Dev Mode
If modifying the React source in `frontend/`:

```bash
cd frontend
npm install
npm run dev
# Vite will launch on http://localhost:5173 with proxy to backend port 8000
```
To compile and build static production assets into `task4_evaluation_and_ui/static/`:
```bash
npm run build
```

---

### Step 8: (Optional) Running Production PostgreSQL & Kafka with Docker
```bash
# Start PostgreSQL, pgAdmin, Zookeeper, and Kafka
docker-compose up -d

# Verify containers are healthy
docker ps
```

---

## 5. Verification, Testing & Evaluation Suites

### 5.1 Run Automated 5-Dimension Evaluation Suite
To execute the comprehensive evaluation benchmark required by Task 4:

```bash
python task4_evaluation_and_ui/evaluate_system.py
```
This runs the full test harness and outputs an evaluation summary covering:
1. Vector Retrieval Hit Rate @ 1, 3, 5 and MRR
2. Supervised ROC-AUC & Isolation Forest Specificity
3. LLM Factual Grounding & Zero-Hallucination Rate
4. Natural Language Intent Classification Accuracy
5. System Latency and Deterministic Consistency

### 5.2 Run API Endpoint Verification Tests
```bash
python task4_evaluation_and_ui/test_api_endpoints.py
```

### 5.3 Run Multi-Agent LangGraph Pipeline Tests
```bash
python task3_multi_agent_system/test_multi_agent.py
```

### 5.4 Run Scikit-Learn Model Unit Tests
```bash
python task2_models_analytics/test_models.py
```

---

## 6. Detailed Feature-by-Feature User Walkthrough

### 1. Claims Explorer & Filter Engine
- **Navigation**: Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
- **Actions**:
  - Filter claims by **Policy Type** (*Auto, Fire/Home, Life, Liability*).
  - Filter by **Risk Tier** (*Low, Medium, High, Critical*) or **Adjudication Status** (*Submitted, Under Investigation, Approved, Rejected, Escalated to SIU*).
  - Search by Claimant Name, Policy ID, or Claim ID in the top search bar.
  - Sort by Loss Amount, Reporting Delay, or Date.

### 2. Multi-Agent Forensic Investigation & Live Dossier
- **Action**: Click on any claim (e.g. `CLM-00002` or `CLM-00003`) or click **Investigate Claim**.
- **Execution**: The LangGraph engine runs concurrent retrieval and risk modeling, synthesizes findings via `gpt-5-nano`, and outputs:
  - **Composite Risk Score Gauge & Anomaly Badge**.
  - **Executive Summary Brief** generated by Agent 4.
  - **Similar Historical Incident Precedents** matched via ChromaDB with similarity percentages.
  - **SIU Forensic Evidence Checklist** generated by Agent 5 if risk threshold (`>= 70%`) is triggered.
  - **Senior Advisor Strategic Inquiries & Directives** generated by Agent 6.

### 3. Human-in-the-Loop Adjudication Gate (Four-Eyes Principle)
- **Action**: In the right-hand panel of the claim dossier, choose an action:
  - **Approve Claim**: Fast-track disbursement for verified legitimate claims.
  - **Reject Claim**: Document formal refusal reason with audit trail.
  - **Escalate to SIU**: Dispatch file to the Special Investigation Unit for forensic field review.
- **Result**: The decision is permanently committed with timestamp and adjuster notes.

### 4. Adjuster AI Copilot Chatbot
- **Navigation**: Click the Chatbot icon in the navbar or navigate to [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat).
- **Capabilities**:
  - Ask natural language portfolio questions: *"Show me the top 5 highest risk claims currently pending review."*
  - Search incident descriptions: *"Find previous claims involving water leakage while the homeowner was on vacation."*
  - Retrieve portfolio KPIs: *"What is our overall claim approval rate and SIU escalation rate?"*
  - Deep-dive into specific claims: *"Why was claim CLM_DIRTY_002 escalated to SIU?"*
- **Mechanism**: The chatbot autonomously determines which tools to execute (`query_claims_db`, `search_incident_precedents`, `get_claim_dossier`, `get_system_kpis`), synthesizes the output, and provides cited claim references.

### 5. Kafka Streaming Ingestion & Sanitation Portal
- **Navigation**: Navigate to [http://127.0.0.1:8000/ingest](http://127.0.0.1:8000/ingest).
- **Capabilities**:
  - **Single Claim Submission Form**: Input custom claim parameters and stream directly into Kafka.
  - **Bulk CSV Upload**: Upload batch claims files (`sample_clean_claims.csv` or `sample_dirty_claims.csv`).
  - **Live Audit Stream**: Real-time log buffer showing message receipt, schema repair, database commit, and vector store embedding.

---

## 7. Complete REST API Reference & Code Examples

### 7.1 Core Claims Endpoints

#### `GET /api/claims`
Returns a paginated list of claims with optional filtering.
- **Parameters**: `policy_type`, `risk_tier`, `status`, `search`, `limit`, `offset`.
- **cURL Example**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/claims?policy_type=Auto&limit=5"
  ```

#### `GET /api/claims/{claim_id}`
Returns complete 360° details of a single claim, customer profile, and investigation history.
- **cURL Example**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/claims/CLM-00002"
  ```

---

### 7.2 Multi-Agent Investigation Endpoints

#### `POST /api/investigate/{claim_id}`
Executes the 6-agent LangGraph workflow on the given claim.
- **cURL Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/investigate/CLM-00003"
  ```
- **Response Sample (JSON)**:
  ```json
  {
    "claim_id": "CLM-00003",
    "customer_id": "CUST-00003",
    "composite_risk_score": 0.88,
    "risk_tier": "Critical",
    "is_anomaly": true,
    "requires_handoff": true,
    "recommendation": "ESCALATE TO SIU",
    "executive_summary": "Claimant filed for €35,000 catastrophic fire damage with a 45-day reporting delay and no emergency dispatch report. Isolation Forest identified a 99th-percentile anomaly.",
    "similar_claims": [
      {
        "claim_id": "CLM-00184",
        "similarity_score": 0.912,
        "incident_type": "Structure Fire",
        "claim_amount": 34200.0,
        "investigation_outcome": "Fraud Confirmed"
      }
    ],
    "siu_evidence_checklist": [
      "CRITICAL: Unreported structural incident exceeding policy reporting threshold (>30 days).",
      "CRITICAL: No official fire department or police dispatch incident number attached.",
      "HIGH: Claim amount (€35,000) exceeds 3x the demographic cohort average (€11,200)."
    ],
    "advisor_guidance": {
      "strategic_summary": "Urgent forensic review required prior to any coverage confirmation.",
      "recommended_action": "Freeze payout and issue formal Proof of Loss questionnaire.",
      "suggested_questions": [
        "Request certified copy of Fire Department incident report #.",
        "Obtain sworn statement explaining the 45-day notification gap."
      ]
    }
  }
  ```

---

### 7.3 Semantic Vector Search Endpoints

#### `POST /api/search/by-text`
Queries ChromaDB for semantic similarity across incident narratives.
- **Payload**:
  ```json
  {
    "query": "Car spun out on icy highway and hit guardrail",
    "limit": 3
  }
  ```
- **cURL Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/search/by-text" \
       -H "Content-Type: application/json" \
       -d '{"query": "Car spun out on icy highway and hit guardrail", "limit": 3}'
  ```

---

### 7.4 Adjudication Decision Endpoints

#### `POST /api/adjuster/decision`
Records a human adjuster sign-off in compliance with the Four-Eyes Principle.
- **Payload**:
  ```json
  {
    "claim_id": "CLM-00002",
    "decision": "Approved",
    "notes": "Verified police report and photographic documentation. Matches historical precedent.",
    "adjuster_name": "Senior Adjuster Jane Doe"
  }
  ```
- **cURL Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/adjuster/decision" \
       -H "Content-Type: application/json" \
       -d '{"claim_id":"CLM-00002","decision":"Approved","notes":"Verified against precedents.","adjuster_name":"Jane Doe"}'
  ```

---

### 7.5 Adjuster AI Copilot Chatbot Endpoints

#### `POST /api/chat/message`
Processes natural language commands using the universal 4-tool LLM agent.
- **Payload**:
  ```json
  {
    "message": "Which claims have a reporting delay over 30 days and no police report?",
    "session_id": "adjuster_session_01"
  }
  ```
- **cURL Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/chat/message" \
       -H "Content-Type: application/json" \
       -d '{"message":"Which claims have a reporting delay over 30 days and no police report?","session_id":"adjuster_session_01"}'
  ```

#### `GET /api/chat/suggestions`
Retrieves quick starter prompt suggestions for adjusters.
- **cURL Example**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/chat/suggestions"
  ```

---

### 7.6 Kafka Streaming Ingestion Endpoints

#### `POST /api/ingest/claim`
Publishes a single raw claim to the Kafka `raw-claims-ingest` topic.
- **Payload**:
  ```json
  {
    "claim_id": "CLM_NEW_9001",
    "customer_id": "CUST_00120",
    "policy_type": "Auto",
    "claim_amount": 14500.0,
    "incident_type": "Collision",
    "incident_severity": "Moderate",
    "incident_date": "2026-09-15",
    "claim_date": "2026-09-17",
    "reporting_delay_days": 2,
    "police_report_filed": "Yes",
    "witness_present": "Yes",
    "incident_description": "Rear-end collision at traffic light during rain."
  }
  ```

#### `POST /api/ingest/bulk`
Uploads a batch CSV file for automated Kafka ingestion and data sanitization.
- **cURL Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/ingest/bulk" \
       -F "file=@sample_dirty_claims.csv"
  ```

#### `GET /api/ingest/logs`
Retrieves live Kafka consumer and sanitation event logs.
- **cURL Example**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/ingest/logs?limit=20"
  ```

---

## 8. Python SDK / Client Usage Example

Here is how to interact with the complete Aegis system using Python:

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Fetch High-Risk Claims
response = requests.get(f"{BASE_URL}/api/claims", params={"risk_tier": "Critical", "limit": 3})
claims = response.json().get("claims", [])
print(f"Found {len(claims)} critical claims.")

if claims:
    target_claim_id = claims[0]["claim_id"]
    print(f"\n--- Investigating Claim {target_claim_id} ---")
    
    # 2. Trigger Multi-Agent LangGraph Pipeline
    inv_response = requests.post(f"{BASE_URL}/api/investigate/{target_claim_id}")
    inv_data = inv_response.json()
    
    print(f"Risk Score: {inv_data.get('composite_risk_score'):.2%}")
    print(f"Recommendation: {inv_data.get('recommendation')}")
    print(f"Executive Summary:\n{inv_data.get('executive_summary')}")
    
    # 3. Ask Copilot Chatbot for Investigation Advice
    chat_response = requests.post(f"{BASE_URL}/api/chat/message", json={
        "message": f"Summarize key forensic flags and suggest next steps for claim {target_claim_id}",
        "session_id": "python_client"
    })
    print(f"\nAI Copilot Reply:\n{chat_response.json().get('reply')}")
```

---

## 9. Troubleshooting & Frequently Asked Questions (FAQ)

### Q1: The web dashboard displays "Vector Engine Not Pre-Warmed" or retrieval errors.
- **Resolution**: Ensure the ChromaDB vector store was created. Run `python task2_models_analytics/build_vector_store.py` to index the 1,800 incident narratives.

### Q2: Kafka is not running locally. Can I still ingest claims?
- **Resolution**: Yes! The `KafkaProducerManager` automatically falls back to an in-memory direct processing queue when a live Kafka broker (`localhost:9092`) is unreachable. Claims will be sanitized, persisted to SQLite, and embedded in ChromaDB transparently.

### Q3: How do I switch from SQLite to PostgreSQL?
- **Resolution**: Update the `DATABASE_URL` in `.env`:
  `DATABASE_URL=postgresql://aegis_user:aegis_secure_password_2026@localhost:5432/aegis_insurance`
  Then run `docker-compose up -d postgres` and restart the application.

### Q4: Are LLM API keys required to run basic ML inference?
- **Resolution**: No. The Random Forest risk model, Isolation Forest anomaly detector, and ChromaDB vector search are 100% deterministic and execute locally without external API calls. The OpenAI API key is only utilized for live natural language executive summaries (`gpt-5-nano`) and the Adjuster Chatbot Copilot.

---

## 10. Summary & Deliverables Verification Table

| Requirement from Project 10 Specification | Corresponding Artifact / Module | Verification Command |
| :--- | :--- | :--- |
| **Task 1 (20%): Data Preparation & Grounding** | `task1_data_preparation/prepare_data.py`<br/>`task1_data_preparation/data_sanitizer.py` | `python task1_data_preparation/prepare_data.py` |
| **Task 2 (25%): Models, Similarity & Risk** | `task2_models_analytics/train_models.py`<br/>`task2_models_analytics/build_vector_store.py` | `python task2_models_analytics/test_models.py` |
| **Task 3 (25%): Multi-Agent Investigation Core** | `task3_multi_agent_system/graph.py`<br/>`task3_multi_agent_system/agents/` | `python task3_multi_agent_system/test_multi_agent.py` |
| **Task 4 (20%): Evaluation & Web Dashboard** | `task4_evaluation_and_ui/evaluate_system.py`<br/>`task4_evaluation_and_ui/static/` | `python task4_evaluation_and_ui/evaluate_system.py` |
| **Task 5 (10%): Architecture & Documentation** | `task5_documentation/ARCHITECTURE.md`<br/>`task5_documentation/USER_GUIDE_AND_EXECUTION.md`<br/>`task5_documentation/PRESENTATION_GUIDE.md` | Inspect documentation files or `/docs` |

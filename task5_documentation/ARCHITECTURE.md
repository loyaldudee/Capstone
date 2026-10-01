# Aegis System Architecture & Technical Specification

## 1. Executive System Overview

**Aegis** is an enterprise-grade AI-powered Insurance Claims Intelligence, Fraud Detection, and Adjudication Decision Support Platform. Grounded in the real-world **COIL 2000 Insurance Benchmark** (9,822 policyholders across 86 socio-demographic features), Aegis combines:

1. **Predictive Machine Learning**: Supervised Random Forest risk classification and unsupervised Isolation Forest multi-variate anomaly detection.
2. **Dense Semantic Retrieval**: High-dimensional vector search with ChromaDB and `sentence-transformers/all-MiniLM-L6-v2`.
3. **Multi-Agent Orchestration (LangGraph)**: A stateful 6-agent LangGraph workflow featuring parallel fan-out execution, live LLM executive synthesis (`gpt-5-nano`), dynamic Agent-to-Agent (A2A) handoffs to a Special Investigation Unit (SIU) support agent, and senior adjudication advisor guidance.
4. **Universal Agentic Chatbot Copilot**: A multi-turn conversational AI engine equipped with 4 deterministic tools for real-time natural language querying across database records, vector embeddings, and portfolio KPIs.
5. **Real-time Event-Driven Streaming Ingestion**: Apache Kafka event pipeline with data quality sanitation, schema validation, and background asynchronous ingestion workers.
6. **Relational Microservice Architecture**: Modular FastAPI service with database-agnostic SQLAlchemy ORM (SQLite for local rapid testing, PostgreSQL with Docker for production).
7. **Human-in-the-Loop Governance**: Full regulatory compliance with the "Four-Eyes Principle" requiring human adjuster adjudication sign-off on all financial disbursements.

---

## 2. High-Level Microservice Architecture Diagram

```mermaid
flowchart TB
    subgraph Client_Layer["Presentation Layer (Clients & Frontends)"]
        WebUI["Aegis Dark-Mode Interactive Dashboard<br/>(Claims Explorer, Dossier, Vector Query, Adjuster Gate)"]
        ReactUI["React / Vite Dashboard & Copilot<br/>(Retro-Pastel Redesign, Advisor Guidance Card)"]
        ChatUI["Adjuster AI Copilot Chat Drawer<br/>(Natural Language Tool Calling & Suggestions)"]
        IngestUI["Kafka Ingestion & Sanitation Portal<br/>(Single Claim Form, CSV Bulk Streamer, Audit Logs)"]
    end

    subgraph API_Gateway["Microservice API Gateway (FastAPI)"]
        Main["main.py<br/>(Lifespan, Static Mount, CORS, Service Registry)"]
        CoreRoutes["routes.py<br/>(/api/claims, /api/investigate, /api/search, /api/adjuster)"]
        IngestRoutes["ingestion_routes.py<br/>(/api/ingest/claim, /api/ingest/bulk, /api/ingest/logs)"]
        ChatRoutes["chat_routes.py<br/>(/api/chat/message, /api/chat/reset, /api/chat/suggestions)"]
        Schemas["schemas.py<br/>(Pydantic v2 DTOs & Validation Contracts)"]
    end

    subgraph Kafka_Bus["Event-Driven Streaming Ingestion (Apache Kafka)"]
        Producer["Kafka Producer Manager<br/>(task1_data_preparation/kafka_service.py)"]
        TopicRaw["Topic: raw-claims-ingest"]
        Consumer["Background Ingestion Worker<br/>(task1_data_preparation/streaming_worker.py)"]
        Sanitizer["Data Sanitizer & Validator<br/>(task1_data_preparation/data_sanitizer.py)"]
    end

    subgraph Agentic_Core["Agentic Intelligence Core (LangGraph StateGraph)"]
        State["ClaimsInvestigationState"]
        
        subgraph Fan_Out_Parallel["Parallel Fan-Out Execution"]
            A1["Agent 1: Retrieval Agent<br/>(ChromaDB Dense Vector Precedents)"]
            A2["Agent 2: Risk Analysis Agent<br/>(Random Forest & Policy Validation)"]
            A3["Agent 3: Anomaly Agent<br/>(Isolation Forest & IQR Outlier Baselines)"]
        end

        subgraph Fan_In_Synthesis["Fan-In & LLM Synthesis"]
            A4["Agent 4: Summarization Agent<br/>(Live gpt-5-nano Executive Brief & Compounding)"]
        end

        subgraph Conditional_Handoff["Dynamic Conditional Edge Routing"]
            Router{"Conditional Edge:<br/>route_handoff()"}
            A5["Agent 5: SIU Investigation Support Agent<br/>(Forensic Evidence Checklist & Action Formulation)"]
            A6["Agent 6: Senior Adjudication Advisor Agent<br/>(Adjuster Copilot & Strategic Guidance)"]
            EndNode(["Auto-Cleared / Adjudication Gate<br/>(END)"])
        end
    end

    subgraph Chatbot_Core["Universal Agentic Chatbot Engine"]
        ChatEngine["chatbot_engine.py<br/>(Multi-Turn Session Memory, Tool Execution)"]
        T1["Tool: query_claims_db"]
        T2["Tool: search_incident_precedents"]
        T3["Tool: get_claim_dossier"]
        T4["Tool: get_system_kpis"]
    end

    subgraph Analytics_Layer["ML & Analytics Engine"]
        RF_Model["Random Forest Risk Classifier<br/>(ROC-AUC: 0.9467, Accuracy: 87.5%)"]
        IF_Model["Isolation Forest Anomaly Detector<br/>(Contamination: 13.4%, Specificity: 90.2%)"]
        Baselines["Policy Cohort Statistical Baselines<br/>(IQR, Z-Score Thresholds)"]
        Embedder["Sentence-Transformers<br/>(all-MiniLM-L6-v2)"]
    end

    subgraph Storage_Layer["Storage & Persistence Layer"]
        ChromaDB[("ChromaDB Vector Store<br/>1,800+ Incident Narrative Embeddings")]
        RelationalDB[("SQLAlchemy RDBMS<br/>SQLite (Default) / PostgreSQL (Production)<br/>Customers, Claims, Investigations, Decisions")]
        GroundTruth[("COIL 2000 Ground Truth Archive<br/>9,822 Profiles / Isolated Evaluation Set")]
    end

    %% Interactions
    WebUI & ReactUI & ChatUI & IngestUI -->|HTTP / JSON| API_Gateway
    Main --> CoreRoutes & IngestRoutes & ChatRoutes
    CoreRoutes --> Schemas & Agentic_Core & RelationalDB
    ChatRoutes --> ChatEngine
    ChatEngine --> T1 & T2 & T3 & T4
    T1 & T3 & T4 --> RelationalDB
    T2 --> ChromaDB
    
    IngestRoutes --> Producer
    Producer --> TopicRaw
    TopicRaw --> Consumer
    Consumer --> Sanitizer
    Sanitizer --> RelationalDB & ChromaDB

    State --> A1 & A2 & A3
    A1 --> Embedder --> ChromaDB
    A2 --> RF_Model
    A3 --> IF_Model & Baselines
    A1 & A2 & A3 --> A4
    A4 --> Router
    Router -->|Risk >= 0.70 OR Policy Coverage Mismatch| A5
    Router -->|Routine Claim: Risk < 0.70| EndNode
    A5 --> A6
    A6 --> EndNode
    EndNode --> RelationalDB
```

---

## 3. Multi-Agent Workflow Specification (LangGraph)

The core decisioning engine operates on a typed state object (`ClaimsInvestigationState`) passing between 6 specialized agents:

```mermaid
sequenceDiagram
    autonumber
    actor Adjuster as Human Claims Adjuster
    participant API as FastAPI Microservice
    participant Graph as LangGraph Orchestrator
    participant A1 as Agent 1: Retrieval
    participant A2 as Agent 2: Risk Analysis
    participant A3 as Agent 3: Anomaly Detection
    participant A4 as Agent 4: Summarization (LLM)
    participant A5 as Agent 5: SIU Support
    participant A6 as Agent 6: Senior Advisor
    participant DB as Relational Database

    Adjuster->>API: POST /api/investigate/{claim_id}
    API->>DB: Fetch Claim & Policyholder Profile
    DB-->>API: Return Claim Data & Demographics
    API->>Graph: invoke(initial_state)

    Note over Graph,A3: Parallel Fan-Out Execution
    par Agent 1 (ChromaDB)
        Graph->>A1: Query Dense Semantic Vectors
        A1-->>Graph: Top-3 Nearest Historical Precedents
    and Agent 2 (Random Forest)
        Graph->>A2: Evaluate Tabular Risk & Active Coverage
        A2-->>Graph: Risk Probability + Policy Verification
    and Agent 3 (Isolation Forest)
        Graph->>A3: Multivariate Outlier Inspection
        A3-->>Graph: Anomaly Flag + IQR Severity Outliers
    end

    Note over Graph,A4: Fan-In Consolidation
    Graph->>A4: Synthesize Specialist Findings
    A4->>A4: Call gpt-5-nano (Live AI Intelligence)
    A4-->>Graph: Executive Brief & Combined Risk Score

    alt Risk Score >= 0.70 OR Coverage Mismatch
        Graph->>A5: Dynamic A2A Handoff (SIU Escalation)
        A5->>A5: Compile Forensic Evidence Checklist
        A5-->>Graph: Action: ESCALATE TO SIU
        Graph->>A6: Invoke Senior Adjudication Advisor
        A6->>A6: Generate Strategic Guidance & Investigation Inquiries
        A6-->>Graph: Strategic Advisor Directives
    else Routine Claim (Risk < 0.70)
        Graph->>A6: Invoke Senior Adjudication Advisor
        A6-->>Graph: Routine Fast-Track Validation Guidance
        Graph-->>Graph: Auto-Cleared (Routine Finish)
    end

    Graph-->>API: Return Final ClaimsInvestigationState
    API->>DB: Store InvestigationRecord (Score, Checklist, Advisor Guidance, Audit Trace)
    API-->>Adjuster: Render Live Dossier, Risk Gauges, SIU Checklist & Advisor Guidance
    
    Adjuster->>API: POST /api/adjuster/decision (Sign-Off)
    API->>DB: Commit AdjusterDecision & Update Claim Status
    API-->>Adjuster: Adjudication Confirmation
```

### Agent Responsibilities & Tool Matrix

| Agent | Module | Primary Role | Tools / Backing Engines |
| :--- | :--- | :--- | :--- |
| **Agent 1: Retrieval** | `retrieval_agent.py` | Finds semantically similar past claims | ChromaDB vector search (`all-MiniLM-L6-v2`) |
| **Agent 2: Risk Analysis** | `risk_analysis_agent.py` | Calculates actuarial fraud probability and validates customer policy registry | Supervised Random Forest Classifier + Policy Registry Lookup |
| **Agent 3: Anomaly Detection** | `anomaly_agent.py` | Discovers multi-dimensional statistical outliers and distribution deviations | Unsupervised Isolation Forest + Historical Statistical Baseline |
| **Agent 4: Summarization** | `summarization_agent.py` | Consolidates specialist inputs and constructs adjuster executive briefs | OpenAI reasoning model (`gpt-5-nano`) |
| **Agent 5: SIU Support** | `investigation_agent.py` | Constructs evidentiary checklists and recommended escalation pathways | Forensic Rule Engine & Checklist Generator |
| **Agent 6: Senior Advisor** | `advisor_agent.py` | Provides strategic claims adjudication directives, inquiry questions, and reviewer fast-track advice | LLM Reasoning & Prompt Optimization Engine |

---

## 4. Universal Agentic Chatbot Engine

The system includes an intelligent natural language chatbot copilot (`chatbot_engine.py` / `chat_routes.py`) that answers complex adjuster questions across 4 deterministic tools:

```mermaid
flowchart LR
    UserPrompt["Adjuster Natural Language Prompt"] --> LLM["LLM Agent (gpt-5-nano)"]
    LLM --> Decision{"Tool Calling Decision"}
    
    Decision -->|Filter & Aggregates| T1["tool_query_claims_db<br/>(Amounts, Delay, Severity, Police Report)"]
    Decision -->|Semantic Precedents| T2["tool_search_incident_precedents<br/>(ChromaDB Vector Similarity)"]
    Decision -->|Deep Dive Dossier| T3["tool_get_claim_dossier<br/>(360° Profile & ML Factors)"]
    Decision -->|Portfolio Metrics| T4["tool_get_system_kpis<br/>(Approval Rate, SIU %, Benchmarks)"]
    
    T1 & T2 & T3 & T4 --> Synthesizer["Contextual Synthesis & Citation Formatter"]
    Synthesizer --> Reply["Structured Response with Cited Claims & Tools Log"]
```

---

## 5. Event-Driven Streaming Ingestion Pipeline (Kafka)

Claims can enter the system via high-throughput real-time Kafka event streams or batch CSV uploads:

```mermaid
sequenceDiagram
    autonumber
    actor ExternalSystem as External Ingestion Source / CSV Upload
    participant API as Ingestion API (/api/ingest/claim)
    participant Producer as KafkaProducerManager
    participant Topic as Kafka Topic (raw-claims-ingest)
    participant Worker as Background Ingestion Worker
    participant Sanitizer as Data Sanitizer & Validator
    participant DB as SQLite / PostgreSQL
    participant VectorStore as ChromaDB

    ExternalSystem->>API: POST /api/ingest/claim (JSON / CSV row)
    API->>Producer: publish_claim_event(payload)
    Producer->>Topic: Emit Raw Ingestion Event
    API-->>ExternalSystem: Return 200 Queued Status
    
    Topic->>Worker: Poll Message Batch
    Worker->>Sanitizer: sanitize_claim_record(payload)
    Sanitizer->>Sanitizer: Fix types, impute defaults, validate policy rules
    Sanitizer-->>Worker: Cleaned & Standardized Claim Entity
    Worker->>DB: Upsert Customer & Claim Record
    Worker->>VectorStore: Embed Description into ChromaDB
    Worker->>Worker: Append Event to INGESTION_LOG_BUFFER
```

---

## 6. Relational Database Schema & Entity Relationships

The relational data model is built database-agnostically with SQLAlchemy. It supports zero-configuration SQLite for development and PostgreSQL for production:

```mermaid
erDiagram
    CUSTOMERS ||--o{ CLAIMS : "owns"
    CLAIMS ||--o{ INVESTIGATION_RECORDS : "generates"
    CLAIMS ||--o{ ADJUSTER_DECISIONS : "adjudicated by"

    CUSTOMERS {
        string customer_id PK
        string customer_subtype
        string customer_main_type
        string age_group
        int purchasing_power_class
        int total_policies_count
        int active_product_lines_count
        boolean has_car_policy
        boolean has_fire_policy
        boolean has_boat_policy
        boolean has_life_policy
        boolean has_accident_policy
    }

    CLAIMS {
        string claim_id PK
        string customer_id FK
        string policy_type
        int policy_count
        int policy_contribution_tier
        int purchasing_power_class
        float claim_amount
        string incident_type
        string incident_severity
        string incident_date
        string claim_date
        int reporting_delay_days
        string police_report_filed
        string witness_present
        int prior_claims_count
        text incident_description
        string claim_status
    }

    INVESTIGATION_RECORDS {
        int id PK
        string claim_id FK
        float composite_risk_score
        string risk_tier
        boolean is_anomaly
        boolean requires_handoff
        string recommendation
        text executive_summary
        text evidence_checklist
        text advisor_guidance
        text audit_log
        datetime investigated_at
    }

    ADJUSTER_DECISIONS {
        int id PK
        string claim_id FK
        string decision
        text notes
        string adjuster_name
        datetime decided_at
    }
```

---

## 7. Data Flow & Zero-Leakage Architecture

A core design requirement was guaranteeing zero data leakage:
1. **Observable Features Only**:
   - The ML models and agents receive **only** observable pre-settlement attributes: `claim_amount`, `reporting_delay_days`, `policy_contribution_tier`, `purchasing_power_class`, `incident_type`, `incident_severity`, `police_report_filed`, `witness_present`, and chronological `prior_claims_count`.
2. **Ground Truth Isolation**:
   - Ground truth labels (`fraud_indicator`, `fraud_reason`, `investigation_outcome`) were strictly isolated into `claims_ground_truth.csv` and are **never** present in the database or passed to agents during inference.
3. **Chronological Calculation**:
   - `prior_claims_count` was computed using chronological windowing (`cumcount()`) ordered by loss date, eliminating temporal lookahead bias.

---

## 8. Security, Compliance & Four-Eyes Governance

- **Human-in-the-Loop (HITL) Gate**: In compliance with insurance regulatory mandates, the multi-agent system does not autonomously disburse payments. It provides evidence, structured recommendations (`Auto-Cleared`, `Documentation Review`, `SIU Escalation`), and strategic advisor questions, requiring an authorized human adjuster to perform final adjudication sign-off.
- **Audit Logging**: Every agent step records its timestamp, role, state transition, and findings into the persistent `audit_log` JSON field, enabling full regulatory explainability.
- **Environment Isolation**: API credentials and database connection strings are strictly managed via `.env` with fallback defaults. Binary models and database files are omitted from git tracking.

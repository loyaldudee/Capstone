# Aegis System Architecture & Technical Specification

## 1. Executive System Overview

**Aegis** is an enterprise-grade AI-powered Insurance Claims Intelligence and Forensic Investigation Assistant. The system combines:
1. **Predictive Machine Learning**: Random Forest risk classification and unsupervised Isolation Forest anomaly detection.
2. **Dense Semantic Retrieval**: High-dimensional vector search with ChromaDB and `all-MiniLM-L6-v2`.
3. **Multi-Agent Orchestration**: A stateful 5-agent LangGraph workflow featuring parallel fan-out execution, live LLM executive synthesis (`gpt-5-nano`), and dynamic Agent-to-Agent (A2A) handoffs to a Special Investigation Unit (SIU) support agent.
4. **Relational Microservice Architecture**: Modular FastAPI service with database-agnostic SQLAlchemy ORM (SQLite locally, PostgreSQL in production).
5. **Human-in-the-Loop Governance**: Compliance with the "Four-Eyes Principle" requiring human adjuster adjudication sign-off on all financial disbursements.

---

## 2. High-Level Microservice Architecture Diagram

```mermaid
flowchart TB
    subgraph Presentation_Layer["Presentation Layer (Client)"]
        UI["Aegis Dark-Mode Dashboard<br/>(HTML5 / CSS3 / Vanilla JS)"]
        CLI["CLI Verification & Test Suite<br/>(pytest / test_api_endpoints.py)"]
    end

    subgraph API_Gateway["Microservice API Gateway (FastAPI)"]
        Main["main.py<br/>(Lifespan, CORS, Static Mount)"]
        Routes["routes.py<br/>(REST Endpoints: /api/claims, /api/investigate, /api/search)"]
        Schemas["schemas.py<br/>(Pydantic v2 DTOs & Validation Contracts)"]
    end

    subgraph Multi_Agent_Core["Agentic Core (LangGraph StateGraph)"]
        Orchestrator["Workflow Orchestrator<br/>(ClaimsInvestigationState)"]
        
        subgraph Fan_Out_Parallel["Parallel Fan-Out Execution"]
            Agent1["Agent 1: Retrieval Agent<br/>(Semantic Vector Query)"]
            Agent2["Agent 2: Risk Analysis Agent<br/>(Supervised Classifier & Policy Validation)"]
            Agent3["Agent 3: Anomaly Agent<br/>(Unsupervised Isolation Forest & IQR Outliers)"]
        end

        subgraph Fan_In_Consolidation["Fan-In & Synthesis"]
            Agent4["Agent 4: Summarization Agent<br/>(Live gpt-5-nano Synthesis & Risk Compounding)"]
        end

        subgraph Dynamic_Handoff["Dynamic Conditional Edge Routing"]
            Router{"Conditional Edge:<br/>route_handoff()"}
            Agent5["Agent 5: SIU Investigation Support Agent<br/>(Forensic Evidence Checklist & Action Formulation)"]
            EndNode(["Auto-Cleared / Adjudication Gate<br/>(END)"])
        end
    end

    subgraph Analytics_Layer["ML & Analytics Engine"]
        RF_Model["Random Forest Risk Classifier<br/>(ROC-AUC: 0.9467, Accuracy: 87.5%)"]
        IF_Model["Isolation Forest Anomaly Detector<br/>(Contamination: 13.4%, Specificity: 90.2%)"]
        Baseline["Policy Cohort Statistical Baselines<br/>(IQR, Z-Score Thresholds)"]
        Embedder["Sentence-Transformers<br/>(all-MiniLM-L6-v2)"]
    end

    subgraph Storage_Layer["Storage & Persistence Layer"]
        ChromaStore[("ChromaDB Vector Store<br/>1,800 Incident Narrative Embeddings")]
        RelationalDB[("SQLAlchemy RDBMS<br/>SQLite (Default) / PostgreSQL (Prod)<br/>Customers, Claims, Investigations, Decisions")]
        KnowledgeBase[("Processed Data Archive<br/>9,822 COIL Profiles / 1,800 Grounded Claims")]
    end

    %% Interactions
    UI -->|HTTP / JSON| Routes
    CLI -->|HTTP / JSON| Routes
    Main --> Routes
    Routes --> Schemas
    Routes --> Orchestrator
    Routes --> RelationalDB

    Orchestrator --> Agent1
    Orchestrator --> Agent2
    Orchestrator --> Agent3

    Agent1 --> Embedder
    Embedder --> ChromaStore

    Agent2 --> RF_Model
    Agent2 --> RelationalDB

    Agent3 --> IF_Model
    Agent3 --> Baseline

    Agent1 --> Agent4
    Agent2 --> Agent4
    Agent3 --> Agent4

    Agent4 --> Router
    Router -->|Risk >= 0.70 OR Policy Coverage Mismatch| Agent5
    Router -->|Routine Claim: Risk < 0.70| EndNode
    Agent5 --> EndNode

    EndNode --> RelationalDB
```

---

## 3. Multi-Agent Workflow Specification (LangGraph)

The core decisioning engine operates on a typed state object (`ClaimsInvestigationState`) passing between 5 specialized agents:

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
    else Routine Claim (Risk < 0.70)
        Graph-->>Graph: Auto-Cleared (Routine Finish)
    end

    Graph-->>API: Return Final ClaimsInvestigationState
    API->>DB: Store InvestigationRecord (Score, Checklist, Audit Trace)
    API-->>Adjuster: Render Live Dossier, Risk Gauges & LLM Brief
    
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

---

## 4. Relational Database Schema & Entity Relationships

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

## 5. Data Flow & Zero-Leakage Architecture

A core design requirement was guaranteeing zero data leakage:
1. **Observable Features Only**:
   - The ML models and agents receive **only** observable pre-settlement attributes: `claim_amount`, `reporting_delay_days`, `policy_contribution_tier`, `purchasing_power_class`, `incident_type`, `incident_severity`, `police_report_filed`, `witness_present`, and chronological `prior_claims_count`.
2. **Ground Truth Isolation**:
   - Ground truth labels (`fraud_indicator`, `fraud_reason`, `investigation_outcome`) were strictly isolated into `claims_ground_truth.csv` and are **never** present in the database or passed to agents during inference.
3. **Chronological Calculation**:
   - `prior_claims_count` was computed using chronological windowing (`cumcount()`) ordered by loss date, eliminating temporal lookahead bias.

---

## 6. Security, Compliance & Four-Eyes Governance

- **Human-in-the-Loop (HITL) Gate**: In compliance with insurance regulatory mandates, the multi-agent system does not autonomously disburse payments. It provides evidence and structured recommendations (`Auto-Cleared`, `Documentation Review`, `SIU Escalation`), requiring an authorized human adjuster to perform final adjudication sign-off.
- **Audit Logging**: Every agent step records its timestamp, role, state transition, and findings into the persistent `audit_log` JSON field, enabling full regulatory explainability.
- **Environment Isolation**: API credentials and database connection strings are strictly managed via `.env` with fallback defaults. Binary models and database files are omitted from git tracking.

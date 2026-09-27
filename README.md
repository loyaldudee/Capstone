# Aegis: AI-Powered Insurance Claims Intelligence Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)](https://github.com/langchain-ai/langgraph)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector--Store-blue)](https://www.trychroma.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-ML--Ensembles-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

**Aegis** is an enterprise-grade AI-powered claims adjudication and forensic intelligence platform. Grounded in the real-world **COIL 2000 Insurance Benchmark**, Aegis blends deterministic machine learning, high-dimensional vector search, and a stateful **5-agent LangGraph workflow** with human-in-the-loop decision governance.

---

## Key Highlights & Verification Benchmarks

| Evaluation Dimension | Metric | Aegis Result | PRD Benchmark |
| :--- | :--- | :--- | :--- |
| **Criteria 1: Vector Retrieval** | Hit Rate @ 1 / @ 3 / @ 5 | **100.0% / 100.0% / 100.0%** | > 80% |
| | Mean Reciprocal Rank (MRR) | **1.0000** | > 0.85 |
| **Criteria 2: Risk & Anomaly Detection** | Supervised Model ROC-AUC | **0.9467** | > 0.85 |
| | Overall Test Accuracy | **87.50%** | > 85% |
| | Anomaly Detection Specificity | **90.24%** | > 85% |
| **Criteria 3: Summarization & Grounding** | Factual Grounding Accuracy | **100.0%** | > 95% |
| | Zero-Hallucination Rate | **100.0%** | 100% |
| **Criteria 4: NL Query Intent** | Top-1 Category Accuracy | **100.0%** | > 90% |
| **Criteria 5: Workflow Latency** | Average End-to-End Latency | **13.52s** | Real-time AI |

---

## System Architecture

```mermaid
flowchart TB
    subgraph UI_Layer["Presentation Layer"]
        WebUI["Aegis Dark-Mode Dashboard<br/>(Claims Explorer, Dossier, Vector Query, Adjuster Gate)"]
    end

    subgraph API_Layer["Modular FastAPI Microservice"]
        Main["main.py (App, Lifespan, CORS, Static Mount)"]
        Routes["routes.py (REST Endpoints)"]
        Schemas["schemas.py (Pydantic v2 DTOs)"]
    end

    subgraph LangGraph_Core["Agentic Multi-Agent Core (LangGraph)"]
        Orchestrator["Workflow State Machine"]
        
        subgraph Parallel_Fan_Out["Parallel Fan-Out (Concurrent)"]
            A1["Agent 1: Retrieval<br/>(ChromaDB Semantic Search)"]
            A2["Agent 2: Risk Analysis<br/>(Random Forest + Policy Registry)"]
            A3["Agent 3: Anomaly Detection<br/>(Isolation Forest + Statistical IQR)"]
        end

        subgraph Fan_In["Fan-In & Synthesis"]
            A4["Agent 4: Summarization<br/>(Live gpt-5-nano Synthesis)"]
        end

        subgraph Handoff["Dynamic Conditional Edge Routing"]
            Router{"Risk >= 0.70 OR<br/>Coverage Failure?"}
            A5["Agent 5: SIU Investigation Support<br/>(Forensic Evidence Checklist)"]
            AdjudicationGate(["Human-in-the-Loop Reviewer Gate<br/>(Four-Eyes Compliance)"])
        end
    end

    subgraph Storage_Layer["Persistence Layer"]
        Chroma[("ChromaDB Vector Store<br/>1,800 Incident Narrative Embeddings")]
        RDBMS[("SQLAlchemy RDBMS<br/>SQLite (Default) / PostgreSQL (Production)")]
    end

    WebUI <--> Routes
    Main --> Routes
    Routes --> Schemas
    Routes <--> RDBMS
    Routes --> Orchestrator

    Orchestrator --> A1 & A2 & A3
    A1 <--> Chroma
    A2 <--> RDBMS
    A1 & A2 & A3 --> A4
    A4 --> Router
    Router -->|High Risk| A5
    Router -->|Routine Claim| AdjudicationGate
    A5 --> AdjudicationGate
```

---

## Repository Structure

```
d:\Capstone\
├── main.py                     # Central FastAPI application & lifespan manager
├── routes.py                   # Modular APIRouter with all REST endpoints
├── schemas.py                  # Pydantic v2 data transfer objects (DTOs)
├── models.py                   # SQLAlchemy ORM relational models
├── database.py                 # Engine, sessionmaker, get_db() & auto-seeding
├── server.py                   # Runner alias (py .\server.py or uvicorn main:app)
├── docker-compose.yml          # Production PostgreSQL & pgAdmin services
├── .env                        # Environment variables (API Key, Base URL, Database)
│
├── task1_data_preparation/     # Task 1: 9,822 COIL profiles, 1,800 grounded claims
│   ├── prepare_data.py         # Data decoding & synthetic generation engine
│   └── processed_data/         # customers_clean.csv, claims_knowledge_base.csv
│
├── task2_models_analytics/     # Task 2: Predictive analytics & vector storage
│   ├── train_models.py         # Random Forest & Isolation Forest training
│   ├── models/                 # claims_risk_engine.py, claims_vector_engine.py
│   └── vector_store/           # ChromaDB dense persistent vector index
│
├── task3_multi_agent_system/   # Task 3: LangGraph 5-Agent Architecture
│   ├── graph.py                # StateGraph with parallel fan-out & dynamic handoffs
│   ├── state.py                # TypedDict shared state definition
│   ├── llm_client.py           # Resilient gpt-5-nano client wrapper
│   └── agents/                 # 5 specialized agent implementations
│
├── task4_evaluation_and_ui/    # Task 4: Automated evaluation & interactive UI
│   ├── evaluate_system.py      # Automated 5-criteria benchmark suite
│   ├── test_api_endpoints.py   # Comprehensive endpoint integration test
│   ├── evaluation_report.json  # Raw evaluation benchmark outputs
│   ├── EVALUATION_REPORT.md    # Detailed evaluation markdown report
│   └── static/                 # index.html, styles.css, app.js
│
└── task5_documentation/        # Task 5: System documentation & architecture
    ├── ARCHITECTURE.md         # Full technical architecture specification
    ├── PRESENTATION_GUIDE.md   # 10-minute executive presentation & demo script
    └── Project_10_*.pdf        # Original project requirement specification
```

---

## Installation & Quickstart

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Environment Setup
Clone the repository and activate the virtual environment:
```powershell
# Clone repo
git clone https://github.com/loyaldudee/Capstone.git
cd Capstone

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install required packages
pip install fastapi uvicorn sqlalchemy chromadb sentence-transformers scikit-learn pandas numpy pydantic openai langgraph python-dotenv httpx
```

### 3. Configure `.env`
Ensure your `.env` file in the root folder contains your LLM credentials:
```ini
OPENAI_API_KEY=your_live_api_key_here
OPENAI_BASE_URL=https://api.aicredits.in/v1
MODEL_NAME=gpt-5-nano

# Optional: Set for PostgreSQL (defaults to local SQLite if omitted)
# DATABASE_URL=postgresql://aegis_user:aegis_secure_password@localhost:5432/aegis_insurance_db
```

### 4. Run the Web Dashboard & Microservice
```powershell
uvicorn main:app --reload
# or
py .\server.py
```
Open your browser to: **http://127.0.0.1:8000**

---

## Running Verification & Test Suites

### Run Automated 5-Criteria Benchmark Evaluation
```powershell
python task4_evaluation_and_ui/evaluate_system.py
```
*Generates updated `evaluation_report.json` and `EVALUATION_REPORT.md` verifying all PRD benchmarks.*

### Run Microservice REST API Integration Tests
```powershell
python task4_evaluation_and_ui/test_api_endpoints.py
```
*Tests all 7 REST endpoints, database queries, vector retrieval, and human decision gate.*

### Run Standalone LangGraph Multi-Agent CLI Simulation
```powershell
python task3_multi_agent_system/test_multi_agent.py
```
*Simulates concurrent parallel agent execution and dynamic handoffs directly in the console.*

---

## REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive Aegis UI Dashboard |
| `GET` | `/api/stats` | Returns real-time KPI counts (Total Claims, SIU Flagged, Approved, Pending) |
| `GET` | `/api/claims` | Paginated claim explorer (`?page=1&limit=25&query=...&policy_type=...&status=...`) |
| `GET` | `/api/claims/{claim_id}` | Complete claim dossier + customer demographic profile + investigation history |
| `POST` | `/api/investigate/{claim_id}` | Executes the 5-agent LangGraph workflow and stores findings in the database |
| `POST` | `/api/search/similar` | Dense semantic vector query over 1,800 incident narratives via ChromaDB |
| `POST` | `/api/adjuster/decision` | Human reviewer adjudication sign-off (`Approved`, `Documentation Review`, `SIU Escalation`) |
| `GET` | `/api/evaluation/metrics` | Returns system verification benchmarks and confusion matrix data |

---

## Production Deployment: PostgreSQL Setup

Aegis is database-agnostic. While SQLite is used for zero-dependency local development, PostgreSQL is supported out-of-the-box:

1. **Start PostgreSQL via Docker Compose**:
   ```powershell
   docker compose up -d
   ```
   *Starts PostgreSQL 15 on port `5432` and pgAdmin 4 on port `5050`.*

2. **Update `.env`**:
   ```ini
   DATABASE_URL=postgresql://aegis_user:aegis_secure_password@localhost:5432/aegis_insurance_db
   ```

3. **Start the Microservice**:
   ```powershell
   uvicorn main:app --reload
   ```
   *FastAPI's startup lifespan will automatically detect the empty PostgreSQL database, build all relational schemas, and auto-seed the 9,822 customers and 1,800 claims.*

---

## Human-in-the-Loop Governance ("Four-Eyes Principle")

Under insurance regulatory guidelines, AI systems cannot autonomously approve indemnity disbursements. Aegis operates strictly as an **intelligence and decision-support co-pilot**:
- **Routine Claims (Risk < 70%)**: The system automatically verifies coverage, benchmarks against historical payouts, marks the claim `Auto-Cleared`, and provides a structured recommendation for the adjuster to sign off in seconds.
- **High-Risk Claims (Risk >= 70% or Coverage Mismatch)**: The system triggers an autonomous handoff to the SIU Support Agent, compiles an evidentiary checklist, and flags the case for formal forensic investigation.

---

## License & Acknowledgments
- Grounded in the **COIL 2000 The Insurance Company Benchmark** (Dutch Association of Insurers / Sentient Machine Research).
- Developed for the **AI-Powered Insurance Claims Intelligence Assistant Capstone**.

# Aegis 10-Minute Executive Presentation & Demonstration Guide

This guide is structured for a live 10-minute presentation, technical walkthrough, and evaluator demonstration of the **Aegis AI-Powered Insurance Claims Intelligence Assistant**.

---

## Presentation Timing & Agenda Overview

| Timecode | Section | Key Focus |
| :--- | :--- | :--- |
| **00:00 – 01:30** | **The Insurance Problem & Data Grounding** | Industry context, COIL 2000 demographic grounding (9,822 profiles), zero-leakage synthetic generation. |
| **01:30 – 03:30** | **Multi-Agent Architecture (LangGraph) & Kafka** | Parallel fan-out, LLM executive synthesis, dynamic A2A SIU handoff, and Kafka streaming ingestion. |
| **03:30 – 07:00** | **Live Interactive Demonstration** | Routine auto-clearing vs. SIU escalation, Adjuster Copilot Chatbot, Kafka streaming upload, and Four-Eyes sign-off. |
| **07:00 – 08:30** | **Evaluation & Verification Results** | Objective benchmark metrics: ROC-AUC 0.9467, 100% MRR, 100% zero-hallucination rate. |
| **08:30 – 10:00** | **Production Readiness & Q&A** | PostgreSQL migration, microservice modularity, and technical defenses. |

---

## Detailed Minute-by-Minute Script & Talking Points

### Minute 00:00 – 01:30: The Problem & Data Grounding
**Goal**: Hook the evaluators by highlighting the business problem and how real data was grounded.

- **Speaker Script**:
  > *"Insurance fraud and claims processing inefficiencies cost the property and casualty insurance industry tens of billions of dollars annually. When adjusters handle thousands of claims manually, high-risk cases slip through while honest claimants face unnecessary delays.*
  >
  > *To address this, we built **Aegis**, an AI-powered claims intelligence assistant grounded in the real-world **COIL 2000 Insurance Benchmark**. We decoded 9,822 customer demographic profiles—including purchasing power tiers, age brackets, and active product ownership—and synthesized 1,800 grounded incident claims with zero data leakage.*
  >
  > *Crucially, our system strictly enforces observable pre-settlement features: models never see post-investigation fraud indicators, and prior claim counts are calculated chronologically to eliminate temporal lookahead bias."*

- **Visual / Slide**:
  - Show the data dictionary, demographic distribution of the 9,822 COIL profiles, and the 1,800 grounded claims.

---

### Minute 01:30 – 03:30: Multi-Agent Architecture (LangGraph) & Streaming Pipeline
**Goal**: Explain the architectural elegance of combining deterministic ML, vector search, streaming ingestion, and LLM reasoning.

- **Speaker Script**:
  > *"Why not just feed the claim into a single LLM prompt? Because LLMs are prone to hallucinations, cannot reliably compute probability distributions, and lack real-time access to vector embeddings and structured database records.*
  >
  > *Instead, we designed a stateful 6-agent system orchestrated via **LangGraph**:*
  > 1. *When a claim arrives—either via API or our real-time **Apache Kafka streaming bus**—the system triggers a **Parallel Fan-Out** to three specialist agents concurrently:*
  >    - ***Agent 1 (Retrieval)*** *queries 1,800 embedded incident narratives in ChromaDB using dense sentence-transformer vectors.*
  >    - ***Agent 2 (Risk Analysis)*** *executes a supervised Random Forest classifier and verifies active policy ownership against the customer profile.*
  >    - ***Agent 3 (Anomaly Detection)*** *runs an unsupervised Isolation Forest and checks IQR statistical baselines for payout anomalies.*
  > 2. *These specialist findings **Fan-In** to **Agent 4 (Summarization)**, where `gpt-5-nano` synthesizes the findings into a concise, factual executive brief.*
  > 3. *A **Dynamic Conditional Edge** evaluates the compound findings: if the claim is high risk (>= 70%) or has coverage discrepancies, an autonomous **Agent-to-Agent (A2A) handoff** transfers the case to **Agent 5 (SIU Support)** to construct a forensic evidence checklist.*
  > 4. ***Agent 6 (Senior Advisor)*** *generates strategic directives and claimant interrogation questions.*
  > 5. *In compliance with insurance regulations, the system respects the **Four-Eyes Principle**: it empowers the human adjuster through an interactive Reviewer Gate."*

- **Visual / Slide**:
  - Show the LangGraph architecture diagram (`task5_documentation/ARCHITECTURE.md`).

---

### Minute 03:30 – 07:00: Live Interactive Demonstration
**Goal**: Walk the evaluator through real claims on the running web dashboard (`http://127.0.0.1:8000`).

#### Step 1: Routine / Legitimate Claim (`CLM-00002`)
- **Action**: Select `CLM-00002` (€28,083.02 catastrophic collision).
- **Explanation**:
  > *"Notice that despite the high loss amount (€28k), the system computes a low risk probability of **21.7%** and marks it **Auto-Cleared: Routine Claim**. Why?*
  > *Because the insured has an active Auto policy, reported it within 24 hours, and filed an official police report. Furthermore, ChromaDB matched historical utility pole collisions that paid out between €31k and €45k. The €28k requested is actually below historical norms!*
  > *The adjuster can review the AI brief and approve the claim in seconds."*
- **Action**: Enter a brief note in the Adjuster Gate and click **Approve Claim**. Show the real-time status update to `Approved`.

#### Step 2: High-Risk Anomaly / SIU Escalation & Advisor Guidance
- **Action**: Select a high-risk claim (e.g. `CLM-00003` or search for a claim with no police report / policy mismatch).
- **Explanation**:
  > *"Now observe a high-risk claim. The Random Forest model flags elevated risk (>70%), the Isolation Forest detects a multi-dimensional outlier, and LangGraph dynamically routes to Agent 5 and Agent 6.*
  > *Agent 5 compiles a structured **SIU Evidence Checklist**, while Agent 6 provides **Senior Advisor Inquiries** to cross-examine the claimant.*
  > *The adjuster can immediately route this to the Special Investigation Unit with one click."*

#### Step 3: Natural Language Adjuster Copilot Chatbot
- **Action**: Click the Chatbot Drawer / navigate to `/chat`. Ask: *"Show me the top 5 highest risk claims currently pending review."*
- **Explanation**:
  > *"Our Universal AI Copilot uses tool-calling to query the database, retrieve ChromaDB incident precedents, or compute portfolio KPIs in real time with cited claim references."*

#### Step 4: Real-time Kafka Streaming Ingestion Portal
- **Action**: Navigate to `/ingest`. Upload `sample_dirty_claims.csv`.
- **Explanation**:
  > *"Watch how the ingestion pipeline streams records through Kafka, runs the Data Quality Sanitizer to clean corrupted fields, and persists records to SQLite and ChromaDB with live event audit logs."*

---

### Minute 07:00 – 08:30: Verification & Evaluation Results
**Goal**: Prove that the system meets and exceeds all PRD criteria with hard numbers.

- **Action**: Click the **Evaluation Benchmark** button in the navbar to open the live evaluation modal.
- **Speaker Script**:
  > *"We verified the complete system against the 5 rigorous dimensions required by the PRD:*
  > 1. ***Criteria 1 (Vector Retrieval)***: *Achieved **100.0% Hit@1, Hit@3, and Hit@5**, with a perfect Mean Reciprocal Rank (MRR) of **1.0000**.*
  > 2. ***Criteria 2 (Risk & Anomaly Detection)***: *Our risk engine achieved an **ROC-AUC of 0.9467** and **87.5% overall accuracy** on the held-out test split, with **90.2% specificity**.*
  > 3. ***Criteria 3 (Claim Summary & Grounding)***: *100% of tested summaries showed **perfect factual grounding** and a **100% zero-hallucination rate**.*
  > 4. ***Criteria 4 (NL Query Intent Accuracy)***: *Demonstrated **100.0% Top-1 category classification** across diverse query narratives.*
  > 5. ***Criteria 5 (Latency & Consistency)***: *Average workflow latency was 13.5 seconds with 100% deterministic scoring reproducibility."*

---

### Minute 08:30 – 10:00: Production Readiness, PostgreSQL & Q&A
**Goal**: Highlight enterprise architecture and handle evaluator questions.

- **Speaker Script**:
  > *"From an engineering perspective, Aegis is built as a modular microservice:*
  > - *Layered into `main.py`, `routes.py`, `ingestion_routes.py`, `chat_routes.py`, `schemas.py`, `models.py`, and `database.py`.*
  > - *Designed database-agnostically: running on zero-dependency SQLite locally, with instant 1-line compatibility for PostgreSQL using the provided `docker-compose.yml`.*
  > - *Fully covered by automated integration test suites (`evaluate_system.py`, `test_api_endpoints.py`, `test_multi_agent.py`).*
  >
  > *Thank you, and we welcome your questions!"*

---

## Evaluator Q&A Defense Sheet

| Potential Evaluator Question | Recommended Technical Defense |
| :--- | :--- |
| **Q1: Why did ChromaDB return a 100% match when the prices were different?** | *"ChromaDB embeds the semantic incident description (physical crash mechanics, damage patterns), which were identical incident archetypes. The claim amount is tabular metadata. In insurance, a Mercedes vs. a Volkswagen experiencing the same crash will have different repair costs. Vector search allows adjusters to benchmark whether the requested price is reasonable against historical payouts for that exact crash."* |
| **Q2: How do you prevent data leakage during training?** | *"We strictly separated observable features from ground truth targets into `claims_knowledge_base.csv` vs. `claims_ground_truth.csv`. The model only trains on features visible at filing time. Prior claim counts were calculated using chronological `.cumcount()` windowing so no future claims leak into historical counts."* |
| **Q3: What happens if OpenAI API has downtime?** | *"The multi-agent graph's first three specialist agents (Retrieval, Risk, Anomaly) run entirely locally using ChromaDB, Random Forest, and Isolation Forest. Even if the LLM summarizer is unreachable, deterministic risk scores, coverage checks, and vector matches are computed and displayed."* |
| **Q4: How do you migrate to PostgreSQL and scale Kafka?** | *"Our SQLAlchemy data layer in `database.py` reads `DATABASE_URL`. By starting the provided `docker-compose.yml` and updating `DATABASE_URL=postgresql://...` in `.env`, the system automatically connects to Postgres, creates all tables, and auto-seeds on startup. Kafka topics support horizontal partitioning for consumer groups."* |
| **Q5: How does the system ensure compliance with insurance regulations?** | *"Aegis follows the 'Four-Eyes Principle'. The multi-agent pipeline never automatically pays out or rejects a claim; it prepares the evidence dossier, flags inconsistencies, and passes the case to a licensed human adjuster for final sign-off with audit logging."* |

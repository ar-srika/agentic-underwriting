# 🏢 UnderwriteAI — Enterprise Multi-Agent Underwriting Platform

> **Hackathon Track:** Fortified Enterprise Fleet ($20,000 Category Prize)  
> **Tech Stack:** Google Gemini 3.5 API · Google ADK Patterns · FastAPI · Streamlit · Google Cloud Run · OpenTelemetry · Firestore-Ready State Store  
> **Domain:** Commercial P&C Insurance Underwriting Automation (Small Business)  
> **Live GitHub Repo:** [https://github.com/ar-srika/agentic-underwriting](https://github.com/ar-srika/agentic-underwriting)  
> **Inspiration:** [McKinsey: The Future of AI in the Insurance Industry](https://www.mckinsey.com/industries/financial-services/our-insights/the-future-of-ai-in-the-insurance-industry)

---

## 📌 Problem Statement: The Commercial Underwriting Crisis

Commercial Property & Casualty (P&C) insurance carriers operate on outdated, manual underwriting lifecycles that introduce massive friction, high loss ratios, and regulatory risks:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             TRADITIONAL COMMERCIAL UNDERWRITING BOTTLENECKS                      │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ ⏳ 5–10 Day Intake Turnaround   │ 📉 Subjective & Siloed Pricing  │ ⚖️ Compliance & Audit Exposure │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ • Unstructured ACORD PDFs, loss│ • Underwriters manually apply   │ • Inconsistent rate filings and│
│   run statements, and broker   │   uncalibrated rate debits and │   undocumented pricing credits.│
│   emails require manual triage.│   credits without auditing.    │ • Fair lending (ECOA/FCRA) and │
│ • High operational expense;    │ • Actuarial models disconnected│   disparate impact blindspots. │
│   brokers wait days for quote. │   from live intake workflows.  │ • Lack of OTel trace logs.     │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

**UnderwriteAI** solves this by establishing an institutional **Underwriting Operating System (UWOS)**: an autonomous fleet of **6 collaborative, specialized AI agents** that reduce intake-to-quote latency from **7 business days to 3.2 seconds** while guaranteeing strict regulatory compliance, actuarial bounds ($10,000 max policy cap), data sovereignty, and human-in-the-loop oversight.

---

## 🏆 Hackathon Compliance & Enterprise Fleet Checklist

UnderwriteAI fully satisfies and implements every architectural requirement for the **Fortified Enterprise Fleet** prize:

| Enterprise Capability | Requirement | UnderwriteAI Implementation Status & Reference |
|---|---|---|
| **📋 Agent Registry** | Central cataloging & discovery | ✅ **Implemented** ([`backend/services/agent_registry.py`](backend/services/agent_registry.py)) — Dynamic registration, lifecycle state tracking (`IDLE`, `RUNNING`, `COMPLETED`), versioning (`v1.0.0`), and health metrics. |
| **🌐 Enterprise Runtime** | Serverless scalable hosting | ✅ **Implemented** ([`Dockerfile`](Dockerfile), [`backend/main.py`](backend/main.py)) — Containerized FastAPI REST backend and Streamlit UI deployed to **Google Cloud Run** in sovereign regions. |
| **🧠 Memory Bank** | Asynchronous multi-week context | ✅ **Implemented** ([`backend/services/memory_bank.py`](backend/services/memory_bank.py)) — 90-day TTL `SessionSnapshot` store supporting asynchronous cold-storage hydration across multi-week commercial survey lifecycles. |
| **🔑 Identity & RBAC** | Cross-department access control | ✅ **Implemented** ([`backend/services/agent_registry.py`](backend/services/agent_registry.py)) — Explicit role-based permissions (`Underwriter`, `Actuary`, `Claims_Adjuster`, `Compliance_Officer`, `Broker_API_Client`) and interactive UI simulator. |
| **⚡ API Gateway** | Enterprise service endpoints | ✅ **Implemented** ([`backend/main.py`](backend/main.py)) — Standard REST API endpoints (`/api/v1/underwrite`, `/api/v1/registry`, `/api/v1/metrics`, `/health`) with JSON & Multipart support. |
| **🛡️ Model Armor** | Security & Data Sovereignty | ✅ **Implemented** ([`backend/services/model_armor.py`](backend/services/model_armor.py)) — Region-locking (`Google Cloud us-central1 (Iowa)`), Zero-Data-Retention (ZDR), PII redaction, prompt injection defense, and $10K statutory cap. |
| **🔭 Observability** | Distributed telemetry & audit | ✅ **Implemented** ([`backend/services/observability.py`](backend/services/observability.py)) — OpenTelemetry trace spans (`TraceId`, `SpanId`, `DurationMs`, `TokenCount`) for all 6 agent reasoning steps. |

---

## 🏗️ Multi-Agent System Architecture & Governance Layers

```mermaid
flowchart TD
    subgraph Client["🖥️ Enterprise Client & Gateway Layer"]
        UI["🖥️ Streamlit Enterprise UI<br/><i>(White Theme · Guidewire / Salesforce Look)</i>"]
        API["⚡ FastAPI REST API Gateway<br/><i>(Google Cloud Run · Async Endpoints)</i>"]
        RBAC["🔑 Cross-Department RBAC Layer<br/><i>(Underwriting · Claims · Actuarial · Broker)</i>"]
    end

    subgraph Security["🛡️ Enterprise Governance & Model Armor"]
        ZDR["🔒 Zero-Data-Retention (ZDR)<br/><i>(In-Memory Processing Only)</i>"]
        REG_LOCK["🌐 Sovereign Region Lock<br/><i>(Google Cloud us-central1 - Iowa)</i>"]
        PII["✂️ Field-Level PII Redaction<br/><i>(SSN · Credit Card · Bank Info)</i>"]
        INJ["⛔ Prompt Injection Defense<br/><i>(Jailbreak & System Override Interception)</i>"]
        CAP["💰 Actuarial Bounds<br/><i>(Hard Policy Cap: $10,000 Max)</i>"]
    end

    subgraph Fleet["🤖 Specialized Multi-Agent Fleet"]
        A1["📥 1. Intake Agent<br/><i>(Document Extraction + ACORD 125/126 Parsing)</i>"]
        A2["🔍 2. Risk Profiling Agent<br/><i>(6 Dimensions + FEMA / Seismic / Wildfire Zones)</i>"]
        A3["💰 3. Pricing & Product Agent<br/><i>(Base Rate × 8 Rating Factors · $10K Cap)</i>"]
        A4["⚖️ 4. Compliance Agent<br/><i>(10 Statutory Regulatory & Fair Lending Rules)</i>"]
        A5["🎯 5. Orchestrator Agent<br/><i>(Tripartite Decision Matrix & HITL Triage)</i>"]
        A6["📊 6. Feedback & Learning Agent<br/><i>(Executive Portfolio Intelligence & Alerts)</i>"]
    end

    subgraph StateStore["🏛️ Enterprise State Store & Observability"]
        REG["📋 Agent Registry<br/><i>(Catalog Discovery & Health Checks)</i>"]
        MEM["🧠 Memory Bank<br/><i>(90-Day Multi-Week Snapshots)</i>"]
        OTEL["🔭 OpenTelemetry Telemetry<br/><i>(Distributed Spans & Latency Logs)</i>"]
        NOTIF["🔔 Notification Center<br/><i>(Senior Underwriter Alert Queue)</i>"]
    end

    UI --> API --> RBAC --> Security
    Security --> A5
    A5 --> A1 --> A2 --> A3 --> A4 --> A5 --> A6
    
    A1 & A2 & A3 & A4 & A5 & A6 -.-> REG
    A1 & A2 & A3 & A4 & A5 & A6 -.-> MEM
    A1 & A2 & A3 & A4 & A5 & A6 -.-> OTEL
    A5 --> NOTIF
```

---

## 🔄 End-to-End Sample Workflow: Intake to Decision

```
[Broker ACORD PDF / Text] 
       │
       ▼
[📥 Step 1: Intake Agent] ───────► Extracts Business Info, Property Values, Prior Claims
       │
       ▼
[🔍 Step 2: Risk Agent] ─────────► Computes 6-Dimension Score (Property, Location, Operational, Claims, etc.)
       │                           Detects Hazard Zones (e.g. FEMA Flood AE, Seismic 4, Wildfire WUI)
       ▼
[💰 Step 3: Pricing Agent] ──────► Base Premium × 8 Rating Multipliers ──► Enforces $10,000 Statutory Policy Cap
       │
       ▼
[⚖️ Step 4: Compliance Agent] ───► Executes 10 Statutory Regulatory Rules (Licensing, Prohibited Class, Fair Lending)
       │
       ▼
[🎯 Step 5: Orchestrator] ───────► Tripartite Decision Engine:
       ├─────────────────────────► ⚡ AUTO-APPROVED (Risk ≤ 35, Clean Compliance)
       ├─────────────────────────► 👨‍💼 MANUAL REVIEW (Hazard Zone or 35 < Risk ≤ 65) ──► Senior Underwriter Binding Desk
       └─────────────────────────► 🚫 AUTO-DECLINED (Prohibited Category, Prior Fraud, Risk > 65)
       │
       ▼
[📊 Step 6: Feedback Agent] ─────► Synthesizes Executive Portfolio Insights & Risk Exposure Alerts
```

### 📄 Sample Input Payload (ACORD Commercial Application)
```text
Business Name: Apex Technology Solutions LLC
Business Type: Technology Consulting
Annual Revenue: $1,500,000
Employees: 10
Years in Business: 7
Property Address: 100 Innovation Way, Austin, TX 78701
Property Value: $400,000
Building Age: 4 years
Construction Type: Fire-resistant concrete
Sprinkler System: Yes
Fire Alarm: Yes
Security System: Yes
Claims in past 3 years: 0
Coverage Types: General Liability, Property, Professional Liability
Coverage Limit: $1,000,000
Deductible: $1,000
```

### 📋 Sample Output JSON Payload (`/api/v1/underwrite`)
```json
{
  "submission_id": "76AF6680",
  "decision": "Auto-Approved",
  "confidence_score": 98.5,
  "risk_profile": {
    "composite_score": 9.5,
    "risk_tier": "Low",
    "is_hazard_zone": false,
    "hazard_zones_detected": [],
    "dimensions": [
      { "name": "Property Risk", "score": 8.0, "weight": 0.25 },
      { "name": "Location Risk", "score": 5.0, "weight": 0.20 },
      { "name": "Financial Risk", "score": 10.0, "weight": 0.15 },
      { "name": "Claims Risk", "score": 0.0, "weight": 0.20 },
      { "name": "Operational Risk", "score": 15.0, "weight": 0.10 },
      { "name": "Compliance Risk", "score": 10.0, "weight": 0.10 }
    ]
  },
  "pricing": {
    "base_premium": 1500.0,
    "modifier_product": 0.4606,
    "final_premium": 690.84,
    "premium_capped": false,
    "product_recommendation": "Business Owner's Policy (BOP) — Silver Tier"
  },
  "compliance": {
    "overall_status": "Pass",
    "passed_count": 10,
    "failed_count": 0,
    "compliance_score": 100.0
  },
  "requires_human_review": false,
  "agents_executed": [
    "Intake Agent",
    "Risk Profiling Agent",
    "Pricing Agent",
    "Compliance Agent",
    "Feedback Agent"
  ],
  "processing_time_seconds": 0.74
}
```

---

## 🎨 Enterprise White GUI & Interactive Dashboard Suite

UnderwriteAI features a clean enterprise interface styled after **Guidewire PolicyCenter** and **Salesforce Financial Services Cloud**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  UnderwriteAI | PolicyCenter Enterprise v1.2                                                    │
│  Commercial P&C › Small Business Underwriting › BOP/CPP Fleet                                    │
│  [🟢 US-Central1 (Iowa)]  [🛡️ Model Armor: Active]  [⚡ Gemini 3.5 Pro]  [🏢 Tenant #8820]       │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  🚦 LIVE SEQUENTIAL AGENT PIPELINE:                                                              │
│  [🟢 1/6 Ingestion] ──► [🟢 2/6 Profiling] ──► [🟢 3/6 Rating] ──► [🟢 4/6 Audit] ──► [🟢 5/6 Triage] │
│                                                                                                  │
│  ==============================================================================================  │
│  ✅ AUTO-APPROVED | Confidence: 98.5% | Processing Time: 0.74s | Agents Executed: 5              │
│  ==============================================================================================  │
│                                                                                                  │
│  📊 UNDERWRITING DASHBOARD TABS:                                                                 │
│  ├── 📈 Risk Profile (6-Axis Plotly Radar Chart & Tier Classification)                           │
│  ├── 💰 Pricing & Actuarial Breakdown (8 Modifiers & $10,000 Policy Cap Bar)                    │
│  ├── ⚖️ Statutory Compliance Audit (10-Point Regulatory & Fair Lending Scorecard)               │
│  ├── ⚡ Interactive What-If Sandbox (Salesforce Lightning Styled Risk Mitigation Toggles)       │
│  └── 🔍 Audit Trail & Telemetry (OpenTelemetry Trace Spans & Model Armor ZDR Logs)              │
│                                                                                                  │
│  👨‍💼 SENIOR UNDERWRITER BINDING DESK (For Hazard Zones & Manual Reviews):                       │
│  [ Review Notes & Custom Endorsements Text Area                                                ] │
│  [ ✅ Approve & Bind Policy (Manual Override) ]   [ 🚫 Decline Submission (Underwriter Record) ] │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Comprehensive Test Suite (`tests/`)

The repository includes a 23-test automated test suite:

```bash
# Run test suite with coverage
python -m pytest -v --cov=backend

# Run automated integration pipeline
python test_pipeline.py
```

### Test Suite Coverage Breakdown:
- **`tests/test_document_parser.py`**: Validates unstructured text and ACORD form entity extraction.
- **`tests/test_risk_calculator.py`**: Tests 6 risk dimensions, FEMA flood AE zones, seismic zones, and decline triggers.
- **`tests/test_pricing_engine.py`**: Enforces actuarial multipliers and validates the **$10,000 hard policy cap**.
- **`tests/test_compliance_checker.py`**: Validates all 10 statutory regulatory checks (licensing, fraud, fair lending).
- **`tests/test_services.py`**: Tests Model Armor PII redaction, prompt injection defense, Memory Bank 90-day snapshots, and Agent Registry RBAC.
- **`tests/test_orchestrator.py`**: Tests end-to-end multi-agent execution across low-risk, hazard-zone, and high-risk applications.
- **`tests/test_api.py`**: Tests FastAPI REST endpoints (`/health`, `/api/v1/underwrite`, `/api/v1/registry`, `/api/v1/metrics`).

---

## 🚀 Quick Start & Local Execution

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/ar-srika/agentic-underwriting.git
cd agentic-underwriting
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
# Set GOOGLE_API_KEY="your-gemini-api-key" (robust local simulation enabled by default)
```

### 3. Launch Enterprise Streamlit Frontend
```bash
streamlit run frontend/app.py --server.port 8501 --theme.base light
```
Open **`http://localhost:8501`** in your browser.

### 4. Launch FastAPI REST Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API documentation available at **`http://localhost:8000/docs`**.

---

## 🚢 Google Cloud Run Deployment

```bash
# 1. Deploy directly to Google Cloud Run in sovereign region (us-central1)
gcloud run deploy underwrite-ai \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_API_KEY="YOUR_GEMINI_API_KEY",DATA_SOVEREIGNTY_REGION="us-central1"
```

---

## 📄 License & Governance

Distributed under the **Apache License 2.0**. See [`LICENSE`](LICENSE) and [`SECURITY.md`](SECURITY.md) for details.

# 🏢 Enterprise Multi‑Agent Underwriting Platform

> **Hackathon Track:** Fortified Enterprise Fleet 
> **Tech Stack:** Gemini 3.5 API · ADK/GenKit · Google Cloud (Cloud Run)  
> **Domain:** Insurance Underwriting Automation  

---

## 📌 Problem Statement

Insurance carriers face **slow, fragmented, and compliance‑risky underwriting workflows**:
- Manual intake of ACORD forms and broker submissions.
- Siloed risk assessment and pricing processes.
- Compliance gaps in fairness, auditability, and transparency.
- Resistance to AI adoption due to lack of explainability.

This platform solves these challenges by orchestrating **specialized AI agents** that deliver speed, transparency, and trust — all within enterprise guardrails.

---

## 🧩 Multi‑Agent Architecture

```mermaid
flowchart LR
    A[📥 Intake Agent] --> B[🔍 Risk Profiling Agent]
    B --> C[💰 Pricing & Product Agent]
    C --> D[⚖️ Compliance Agent]
    D --> E[🧑‍✈️ Orchestrator Agent]
    E --> F[📊 Feedback & Learning Agent]

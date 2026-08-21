# 🛡️ Security & Data Sovereignty Policy

UnderwriteAI is designed to operate on production-grade commercial insurance submissions, handling sensitive corporate financials, property locations, loss histories, and proprietary rating algorithms.

---

## 🔒 Security Architecture & Guardrails

1. **Model Armor**:
   - **Inline PII Redaction**: Automatic redaction of SSNs, credit card numbers, and banking details before prompt synthesis.
   - **Prompt Injection Defense**: Multi-pattern jailbreak and instruction override interception.
   - **Actuarial Boundary Enforcement**: Hardware-guaranteed pricing floors ($500) and statutory ceilings (**$10,000**).

2. **Data Sovereignty & Zero-Data-Retention (ZDR)**:
   - All AI inferences and API calls are region-locked to sovereign cloud zones (`Google Cloud us-central1 (Iowa)` / `eu-west3`).
   - Customer data is processed strictly in-memory during active sessions. Zero applicant payload data is retained for foundation model training.

3. **Auditability & Traceability**:
   - OpenTelemetry distributed trace spans are generated for every agent node execution, capturing latency, token usage, and deterministic reasoning chains.

---

## 🚨 Reporting a Vulnerability

If you discover a potential security vulnerability, prompt injection bypass, or data leakage flaw in UnderwriteAI, please report it responsibly:

- **Email**: `security@underwriteai.enterprise.internal`
- **Response SLA**: 24 business hours for initial acknowledgment, 72 business hours for triage and fix timeline.
- Please do **not** file public GitHub issues for critical security vulnerabilities.

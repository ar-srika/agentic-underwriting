# 🤝 Contributing to UnderwriteAI

Thank you for your interest in contributing to **UnderwriteAI**! This project is an enterprise multi-agent insurance underwriting operating system built for production reliability, fair lending compliance, and institutional scale.

---

## 🏛️ Guiding Principles

1. **Deterministic Guardrails First**: Actuarial ratings, compliance checks, and pricing caps ($10,000 max) must remain deterministic and auditable.
2. **Data Sovereignty & Privacy**: All agent processing strictly adheres to Zero-Data-Retention (ZDR) and regional locking (`Google Cloud us-central1`).
3. **Enterprise UX**: Maintain clean, high-density white enterprise styling matching Guidewire PolicyCenter and Salesforce Financial Services Cloud.

---

## 🚀 Development Setup

### 1. Clone and Install
```bash
git clone https://github.com/YOUR_ORGANIZATION/agentic-underwriting.git
cd agentic-underwriting

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env to add your GOOGLE_API_KEY (optional, local simulation fallback enabled)
```

---

## 🧪 Testing Guidelines

Every change must pass our test suite before submitting a PR:

```bash
# Run complete test suite with coverage
pytest -v --cov=backend

# Run integration pipeline verification
python test_pipeline.py
```

---

## 🎨 Code Style & Standards

We enforce modern Python conventions:
- Python 3.10+ type annotations throughout.
- Format with **Black** (100 char line length) and lint with **Ruff**.
- Meaningful commit messages following conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.

---

## 📬 Pull Request Workflow

1. Fork the repository and create a feature branch (`git checkout -b feat/my-enhancement`).
2. Make your changes and write corresponding unit tests under `tests/`.
3. Verify that `pytest` and `python test_pipeline.py` pass without errors.
4. Commit your changes with signed commits (`git commit -s -m "feat: add underwriting rule"`).
5. Push to your fork and submit a PR against `main`.

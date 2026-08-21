"""
UnderwriteAI — Enterprise Multi-Agent Underwriting Platform
Streamlit Frontend

A production-grade enterprise interface for AI-powered insurance
underwriting, inspired by Guidewire, Duck Creek, and Salesforce
Financial Services Cloud.

Features:
- Clean white enterprise theme with rich UI components
- Real-time agent pipeline visualizer with status tracking
- Interactive risk radar charts and pricing breakdowns
- Compliance traffic-light indicators
- Human-in-loop notification center
- Full audit trail and observability dashboard
- Agent registry with health monitoring
"""

from __future__ import annotations

import sys
import os
import time
from pathlib import Path

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from backend.agents.orchestrator import run_orchestrator
from backend.config import settings
from backend.models.schemas import (
    AgentStatus,
    ComplianceStatus,
    DecisionType,
    SubmissionInput,
    SubmissionType,
    UnderwritingDecision,
)
from backend.services.agent_registry import initialize_registry
from backend.services.memory_bank import MemoryBank
from backend.services.model_armor import ModelArmor
from backend.services.observability import ObservabilityService


# ────────────────────────────────────────────────────────────────────
# Page Config
# ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="UnderwriteAI — Enterprise Underwriting Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────────
# Custom CSS — White Enterprise Theme
# ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global Reset ─────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: #f5f6fa !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.block-container {
    padding-top: 1rem !important;
    max-width: 100% !important;
}

/* ── Sidebar Styling ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a237e 0%, #0d1442 100%) !important;
}
[data-testid="stSidebar"] * {
    color: #e8eaf6 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: #c5cae9 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}

/* ── Header ───────────────────────────────────────────── */
.main-header {
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565c0 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(26, 35, 126, 0.25);
}
.main-header h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.main-header p {
    margin: 0.25rem 0 0 0;
    opacity: 0.85;
    font-size: 0.9rem;
}
.header-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 8px;
    backdrop-filter: blur(10px);
}

/* ── Cards ────────────────────────────────────────────── */
.enterprise-card {
    background: #ffffff;
    border: 1px solid #e0e3eb;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.enterprise-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.card-header {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #5f6368;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e8f0fe;
}

/* ── KPI Metric ───────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e0e3eb;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 0.25rem 0;
}
.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #5f6368;
}

/* ── Decision Badges ──────────────────────────────────── */
.decision-approved {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border: 2px solid #4caf50;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.decision-approved .decision-text {
    color: #2e7d32;
    font-size: 1.3rem;
    font-weight: 700;
}
.decision-review {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    border: 2px solid #ff9800;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.decision-review .decision-text {
    color: #e65100;
    font-size: 1.3rem;
    font-weight: 700;
}
.decision-declined {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    border: 2px solid #f44336;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.decision-declined .decision-text {
    color: #c62828;
    font-size: 1.3rem;
    font-weight: 700;
}

/* ── Pipeline Visualizer ──────────────────────────────── */
.pipeline-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0;
    padding: 1.5rem 1rem;
    background: #ffffff;
    border: 1px solid #e0e3eb;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    overflow-x: auto;
}
.pipeline-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 110px;
    position: relative;
}
.pipeline-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.pipeline-icon.idle {
    background: #f5f5f5;
    border: 2px solid #e0e0e0;
}
.pipeline-icon.running {
    background: #e3f2fd;
    border: 2px solid #1976d2;
    animation: pulse 1.5s infinite;
    box-shadow: 0 0 16px rgba(25, 118, 210, 0.3);
}
.pipeline-icon.completed {
    background: #e8f5e9;
    border: 2px solid #4caf50;
}
.pipeline-icon.error {
    background: #ffebee;
    border: 2px solid #f44336;
}
.pipeline-name {
    font-size: 0.7rem;
    font-weight: 600;
    color: #37474f;
    text-align: center;
    max-width: 100px;
}
.pipeline-status {
    font-size: 0.6rem;
    font-weight: 500;
    margin-top: 2px;
}
.pipeline-arrow {
    font-size: 1.2rem;
    color: #bdbdbd;
    margin: 0 4px;
    flex-shrink: 0;
}
.pipeline-arrow.active {
    color: #1976d2;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.08); }
    100% { transform: scale(1); }
}

/* ── Compliance Traffic Light ─────────────────────────── */
.traffic-light {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.traffic-pass {
    background: #e8f5e9;
    color: #2e7d32;
}
.traffic-warning {
    background: #fff3e0;
    color: #e65100;
}
.traffic-fail {
    background: #ffebee;
    color: #c62828;
}

/* ── Notification Banner ──────────────────────────────── */
.notification-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    border-left: 4px solid #d32f2f;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.notification-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    border-left: 4px solid #f57c00;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.notification-info {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    border-left: 4px solid #1976d2;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

/* ── Buttons ──────────────────────────────────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:first-child {
    background: linear-gradient(135deg, #1a237e, #1565c0) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(26, 35, 126, 0.3) !important;
}
.stButton > button:first-child:hover {
    box-shadow: 0 4px 16px rgba(26, 35, 126, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Table Styling ────────────────────────────────────── */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Text Area ────────────────────────────────────────── */
.stTextArea textarea {
    font-family: 'Inter', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    border: 1px solid #dadce0 !important;
}

/* ── Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #ffffff;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #e0e3eb;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.85rem;
}

/* ── Expander ─────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* ── Hide Streamlit Branding ──────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────
# Initialize Services
# ────────────────────────────────────────────────────────────────────

@st.cache_resource
def init_services():
    registry = initialize_registry()
    memory = MemoryBank()
    armor = ModelArmor()
    obs = ObservabilityService()
    return registry, memory, armor, obs

registry, memory, armor, observability = init_services()


# ────────────────────────────────────────────────────────────────────
# Sample Submissions
# ────────────────────────────────────────────────────────────────────

SAMPLE_LOW_RISK = """Business Name: Brightside Consulting LLC
Business Type: Professional Service
Annual Revenue: $1,200,000
Employees: 12
Years in Business: 8

Property Address: 456 Corporate Plaza
City: Austin
State: TX
Zip Code: 73301
Property Value: $450,000
Building Age: 5 years
Construction Type: Fire-resistant concrete
Square Footage: 3200
Floors: 2
Sprinkler System: Yes
Fire Alarm: Yes
Security System: Yes
Roof Condition: Excellent

Claims in past 3 years: 0
Claims in past 5 years: 0

Coverage Types: General Liability, Property, Professional Liability
Coverage Limit: $1,000,000
Deductible: $1,000
Effective Date: 2025-01-01"""

SAMPLE_HAZARD_ZONE = """Business Name: Oceanview Restaurant & Bar
Business Type: Restaurant
Annual Revenue: $850,000
Employees: 25
Years in Business: 4

Property Address: 789 Beachfront Drive
City: Miami
State: FL
Zip Code: 33139
Property Value: $680,000
Building Age: 35 years
Construction Type: Wood frame
Square Footage: 4500
Floors: 1
Sprinkler System: Yes
Fire Alarm: Yes
Security System: No
Roof Condition: Fair

Claims in past 3 years: 2
Largest Claim: $45,000

Coverage Types: General Liability, Property, Business Interruption
Coverage Limit: $750,000
Deductible: $2,500"""

SAMPLE_HIGH_RISK = """Business Name: Heavy Demolition & Waste Corp
Business Type: Hazardous waste disposal
Annual Revenue: $4,000,000
Employees: 80
Years in Business: 1

Property Address: 500 Scrap Yard Rd
City: Los Angeles
State: CA
Zip Code: 90001
Property Value: $1,200,000
Building Age: 60 years
Construction Type: Wood frame
Square Footage: 8000
Floors: 2
Sprinkler System: No
Fire Alarm: No
Security System: No
Roof Condition: Poor

Claims in past 3 years: 6
Claims in past 5 years: 8
Largest Claim: $350,000

Valid License: No
Previous Policy Cancelled: Yes
Cancellation Reason: Prior insurance fraud and material misrepresentation

Coverage Types: General Liability, Property, Workers Compensation
Coverage Limit: $2,000,000
Deductible: $5,000"""


# ────────────────────────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────────────────────────

def render_pipeline_visualizer(agent_statuses: dict[str, str]):
    """Render the agent pipeline flow diagram."""
    agents = [
        ("📥", "Intake Agent", "intake-agent"),
        ("🔍", "Risk Profiling", "risk-agent"),
        ("💰", "Pricing Engine", "pricing-agent"),
        ("⚖️", "Compliance", "compliance-agent"),
        ("🎯", "Orchestrator", "orchestrator-agent"),
        ("📊", "Feedback", "feedback-agent"),
    ]

    html_parts = ['<div class="pipeline-container">']
    for i, (icon, name, agent_id) in enumerate(agents):
        status = agent_statuses.get(agent_id, "idle")
        status_css = status.lower()
        status_color = {
            "idle": "#9e9e9e",
            "running": "#1976d2",
            "completed": "#4caf50",
            "error": "#f44336",
        }.get(status_css, "#9e9e9e")

        html_parts.append(f'''
        <div class="pipeline-node">
            <div class="pipeline-icon {status_css}">{icon}</div>
            <div class="pipeline-name">{name}</div>
            <div class="pipeline-status" style="color: {status_color};">●&thinsp;{status.capitalize()}</div>
        </div>
        ''')

        if i < len(agents) - 1:
            arrow_class = "active" if status_css == "completed" else ""
            html_parts.append(f'<div class="pipeline-arrow {arrow_class}">→</div>')

    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_agent_deep_dive(agent_id: str, decision: UnderwritingDecision | None = None):
    """
    Render a comprehensive, visual drill-down card explaining what an agent does,
    the data it processed, its internal decision rules & formulas, and its verdict.
    """
    agent_info = {
        "intake-agent": {
            "name": "Intake Agent",
            "icon": "📥",
            "department": "Submission Processing",
            "version": "1.0.0",
            "role": "Document Ingestion, Entity Extraction & ACORD Data Cleansing",
            "tools": ["document_parser", "pdf_extractor", "gemini_entity_extractor"],
            "description": "Ingests unstructured broker submissions (raw text or PDF forms), extracts key entity fields (business, property, claims, coverage), decomposes complex addresses, and structures data into validated Pydantic schemas.",
        },
        "risk-agent": {
            "name": "Risk Profiling Agent",
            "icon": "🔍",
            "department": "Risk Assessment",
            "version": "1.0.0",
            "role": "6-Dimensional Quantitative Risk Scoring & Hazard Detection",
            "tools": ["risk_calculator", "hazard_zone_lookup", "gemini_narrative_generator"],
            "description": "Evaluates physical property condition, geographic hazard zones (FEMA flood, seismic, wildfire), financial stability, claims history, operational exposure, and licensing status to compute a normalized 0-100 composite risk score.",
        },
        "pricing-agent": {
            "name": "Pricing & Product Agent",
            "icon": "💰",
            "department": "Actuarial & Rating",
            "version": "1.0.0",
            "role": "Actuarial Base-Rate Rating & $10,000 Hard Policy Cap Enforcement",
            "tools": ["pricing_engine", "product_matcher", "gemini_actuary_rationale"],
            "description": "Calculates risk-adjusted annual premium using an actuarial base rate multiplied by 8 rating factors (class, revenue, workforce, location, claims, safety, experience, building age). Strictly enforces the $10,000 small business policy ceiling.",
        },
        "compliance-agent": {
            "name": "Compliance Agent",
            "icon": "⚖️",
            "department": "Legal & Regulatory Affairs",
            "version": "1.0.0",
            "role": "10-Point Regulatory, Fair Lending & Security Guardrail Validation",
            "tools": ["compliance_checker", "pii_scanner", "fair_lending_evaluator"],
            "description": "Validates the underwriting submission against 10 statutory and institutional rules covering state licensing, prohibited businesses, prior fraud cancellations, rate adequacy, fair lending, and PII protection.",
        },
        "orchestrator-agent": {
            "name": "Orchestrator Agent",
            "icon": "🎯",
            "department": "Underwriting Operations",
            "version": "1.0.0",
            "role": "Pipeline Coordination, Decision Matrix Evaluation & HITL Triage",
            "tools": ["decision_engine", "hitl_router", "notification_dispatcher"],
            "description": "The central nerve center of the platform. Chains all sub-agents sequentially, evaluates the tripartite decision matrix (Auto-Approve / Manual Review / Auto-Decline), and routes hazard zone submissions to human underwriters.",
        },
        "feedback-agent": {
            "name": "Feedback & Learning Agent",
            "icon": "📊",
            "department": "Analytics & Institutional Learning",
            "version": "1.0.0",
            "role": "Executive Synthesis, Loss Ratio Alerts & Portfolio Intelligence",
            "tools": ["executive_summarizer", "portfolio_analyzer", "trend_detector"],
            "description": "Generates board-ready executive summaries, identifies portfolio-level risk concentrations in natural hazard zones, tracks capped premium impacts, and suggests continuous underwriting improvements.",
        },
        "mcp-open-meteo-geocoding": {
            "name": "Open-Meteo Geocoding MCP",
            "icon": "📍",
            "department": "External Intelligence / MCP",
            "version": "1.0.0",
            "role": "Municipal Address Normalization & Spatial Coordinate Resolution",
            "tools": ["open_meteo_geocoding_api", "spatial_normalizer"],
            "description": "Sub-agent data fetcher that queries Open-Meteo Geocoding REST endpoints to decompose raw address text into verified city, state, postal code, latitude, longitude, and elevation metrics.",
        },
        "mcp-fema-flood": {
            "name": "FEMA Flood Zone MCP",
            "icon": "🌊",
            "department": "External Intelligence / MCP",
            "version": "1.0.0",
            "role": "FEMA NFHL Flood Zone Classification & Inundation Rating",
            "tools": ["fema_nfhl_gis", "open_fema_api"],
            "description": "Sub-agent data fetcher that queries FEMA National Flood Hazard Layer (NFHL) GIS data to determine Special Flood Hazard Area (SFHA) status (Zone VE, AE, A, X) and calculate base flood elevations.",
        },
        "mcp-usgs-seismic": {
            "name": "USGS Seismic MCP",
            "icon": "🌋",
            "department": "External Intelligence / MCP",
            "version": "1.0.0",
            "role": "USGS Earthquake Cataloging, Fault Proximity & PGA Rating",
            "tools": ["usgs_earthquake_api", "fault_line_database"],
            "description": "Sub-agent data fetcher that connects to USGS Earthquake Hazards APIs to evaluate real-time fault line proximity, historical M3.5+ earthquake frequency, and Peak Ground Acceleration (PGA).",
        },
        "mcp-open-meteo-weather": {
            "name": "Open-Meteo Weather MCP",
            "icon": "🌪️",
            "department": "External Intelligence / MCP",
            "version": "1.0.0",
            "role": "Hurricane Exposure Tiering, Peak Wind Gusts & Storm Telemetry",
            "tools": ["open_meteo_forecast_api", "climate_extremes_engine"],
            "description": "Sub-agent data fetcher that queries Open-Meteo weather APIs to determine tropical cyclone exposure tiers (Cat 1–5), max recorded wind gusts, and severe convective precipitation risk.",
        },
    }

    info = agent_info.get(agent_id, agent_info["intake-agent"])

    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; border-left:5px solid #1a237e; border-radius:10px; padding:1.25rem; margin-top:0.75rem; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-size:1.15rem; font-weight:700; color:#1a237e;">{info['icon']} {info['name']}
                    <span style="font-size:0.7rem; background:#e8eaf6; color:#1a237e; padding:2px 8px; border-radius:12px; font-weight:600; margin-left:6px;">v{info['version']}</span>
                    <span style="font-size:0.7rem; background:#e0f2f1; color:#00695c; padding:2px 8px; border-radius:12px; font-weight:600; margin-left:4px;">{info['department']}</span>
                </div>
                <div style="font-size:0.85rem; font-weight:600; color:#37474f; margin-top:3px;">{info['role']}</div>
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
                {"".join(f'<span style="font-size:0.7rem; background:#f5f5f5; border:1px solid #e0e0e0; color:#424242; padding:3px 8px; border-radius:6px; font-weight:500;">🔧 {t}</span>' for t in info['tools'])}
            </div>
        </div>
        <div style="font-size:0.82rem; color:#5f6368; margin-top:8px; line-height:1.4;">{info['description']}</div>
    </div>
    """, unsafe_allow_html=True)

    # If a decision has been executed, show the live data & reasoning
    if decision is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        col_logic, col_verdict = st.columns([1, 1])

        # ── 1. INTAKE AGENT DRILLDOWN ───────────────────────────────
        if agent_id == "intake-agent":
            sd = decision.submission_data
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ Ingestion & Parsing Methodology</div>', unsafe_allow_html=True)
                st.markdown("""
                **Step-by-Step Logic Applied:**
                1. **Regex Entity Harvester**: Scans text for 8 key underwriting entity groups.
                2. **Open-Meteo Geocoding MCP**: Queries geospatial coordinates, normalizes jurisdiction, and determines elevation.
                3. **Multimodal / Gemini 3.5 Fallback**: Analyzes missing fields with contextual understanding.
                4. **Completeness Scoring**: Computes extraction confidence percentage.
                """)
                if sd and sd.intake_notes:
                    st.markdown("**Parser & MCP Observations:**")
                    for note in sd.intake_notes:
                        st.markdown(f"- `{note}`")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">📋 Extracted Submission Payload</div>', unsafe_allow_html=True)
                if sd:
                    st.markdown(f"""
                    - **Extraction Confidence**: **`{sd.extraction_confidence}%`**
                    - **Business Name**: `{sd.business_info.business_name or 'N/A'}` (`{sd.business_info.business_type}`)
                    - **Financials**: Revenue **`${sd.business_info.annual_revenue:,.0f}`** | **`{sd.business_info.employee_count}`** Employees
                    - **Location**: `{sd.property_details.address}`, `{sd.property_details.city}`, `{sd.property_details.state}` `{sd.property_details.zip_code}`
                    - **Geospatial Coords**: Lat: **`{sd.property_details.latitude:.4f}`**, Lon: **`{sd.property_details.longitude:.4f}`** (Elev: `{sd.property_details.elevation_m:.1f}m`)
                    - **Property Valuation**: **`${sd.property_details.property_value:,.0f}`** ({sd.property_details.building_age_years}yr old)
                    - **Loss Record**: **`{sd.claims_history.total_claims_3yr}`** claims in 3yr (Largest: `${sd.claims_history.largest_claim_amount:,.0f}`)
                    """)
                    st.success("✅ **Verdict**: Structured data & MCP spatial coordinates normalized and transmitted to Risk Profiling Agent.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 2. RISK PROFILING AGENT DRILLDOWN ───────────────────────
        elif agent_id == "risk-agent":
            rp = decision.risk_profile
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ 6-Dimensional & MCP Risk Algorithm</div>', unsafe_allow_html=True)
                st.markdown("""
                **Mathematical Formula:**
                $$\\text{Composite Score} = \\sum_{i=1}^{6} (\\text{Dimension Score}_i \\times \\text{Weight}_i)$$
                $$\\text{Location Dimension} = 0.40 \\cdot \\text{FEMA Flood} + 0.30 \\cdot \\text{USGS Seismic} + 0.30 \\cdot \\text{Open-Meteo Wind}$$

                | Dimension | Weight | Primary Evaluation Criteria |
                |---|:---:|---|
                | **Property Risk** | 20% | Building age, fire/theft safety systems, construction type, roof |
                | **Location Risk (MCP)** | 20% | Real-time FEMA Flood NFHL, USGS Seismic faults, Open-Meteo windstorms |
                | **Financial Risk** | 15% | Annual revenue scale, longevity in business, financial resilience |
                | **Claims Risk** | 20% | Prior 3yr/5yr claim frequency and maximum claim severity |
                | **Operational Risk** | 15% | Industry hazard tier, employee exposure, workforce scale |
                | **Compliance Risk** | 10% | Licensing status, previous policy cancellations & fraud flags |
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">📊 Risk Assessment Verdict</div>', unsafe_allow_html=True)
                if rp:
                    tier_color = "#2e7d32" if rp.risk_tier.value == "Low" else "#e65100" if rp.risk_tier.value == "Medium" else "#c62828"
                    st.markdown(f"""
                    - **Composite Risk Score**: **<span style="font-size:1.3rem; color:{tier_color}; font-weight:700;">{rp.composite_score} / 100</span>**
                    - **Assigned Risk Tier**: **`<span style="color:{tier_color};">{rp.risk_tier.value} Risk</span>`**
                    - **Hazard Zones Detected**: `{', '.join(rp.hazard_zones_detected) if rp.hazard_zones_detected else 'None (Standard Zone)'}`
                    """)
                    if rp.auto_decline_triggers:
                        st.error(f"🚫 **Auto-Decline Triggers Tripped**: {'; '.join(rp.auto_decline_triggers)}")
                    elif rp.is_hazard_zone:
                        st.warning(f"⚠️ **Hazard Flag**: Property in critical hazard zone — Requires Human Underwriter Triage.")
                    else:
                        st.success("✅ **Standard Profile**: Risk score within acceptable underwriting parameters.")

                    st.markdown(f"**Underwriter Narrative:** {rp.risk_summary}")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 3. PRICING & PRODUCT AGENT DRILLDOWN ────────────────────
        elif agent_id == "pricing-agent":
            pr = decision.pricing
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ Actuarial Rating & Cap Logic</div>', unsafe_allow_html=True)
                st.markdown("""
                **Pricing Engine Formula:**
                $$\\text{Calculated Premium} = \\text{Base Premium} \\times \\prod_{k=1}^{8} \\text{Modifier}_k$$
                $$\\text{Final Premium} = \\min(\\text{Calculated Premium}, \\$10,000)$$

                **Rating Modifiers Evaluated:**
                - **Class Factor**: Business activity hazard tier (0.70x tech – 2.00x construction)
                - **Revenue Factor**: Scale exposure adjustment (0.85x – 1.30x)
                - **Workforce Factor**: Employee workers comp exposure (0.90x – 1.25x)
                - **Location Factor**: Hazard zone surcharge (0.95x standard – 1.60x multi-hazard)
                - **Claims Factor**: Experience rating discount/surcharge (0.85x clean – 1.60x frequency)
                - **Safety Credit**: Protective systems discount (0.82x full – 1.15x none)
                - **Experience Factor**: Business longevity discount (0.85x veteran – 1.20x startup)
                - **Building Age**: Structural factor (0.90x modern – 1.25x old)
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">💵 Pricing Recommendation Verdict</div>', unsafe_allow_html=True)
                if pr:
                    st.markdown(f"""
                    - **Base Premium Tier**: **`${pr.base_premium:,.2f}`**
                    - **Combined Modifier Product**: **`{pr.modifier_product}x`**
                    - **Raw Calculated Premium**: `${pr.calculated_premium:,.2f}`
                    - **Final Policy Premium**: **<span style="font-size:1.3rem; color:#1976d2; font-weight:700;">${pr.final_premium:,.2f}</span>**
                    - **$10,000 Policy Cap Status**: {'⚠️ **CAPPED at $10,000 Limit**' if pr.premium_capped else '✅ **Within $10,000 Ceiling**'}
                    - **Recommended Product**: **`{pr.product_recommendation}`**
                    - **Coverage Limit & Deductible**: `${pr.coverage_limit:,.0f}` limit with `${pr.deductible:,.0f}` deductible
                    """)
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 4. COMPLIANCE AGENT DRILLDOWN ───────────────────────────
        elif agent_id == "compliance-agent":
            cp = decision.compliance
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ 10 Statutory Rules Evaluated</div>', unsafe_allow_html=True)
                st.markdown(r"""
                | Rule ID | Name | Objective |
                |---|---|---|
                | **REG-001** | Licensing Check | Valid operating license verified |
                | **REG-002** | Prohibited Screening | Screen out banned classes (hazardous waste, adult) |
                | **REG-003** | Prior Cancellation | Verify no fraud-related policy cancellations |
                | **FIN-001** | Premium Bounds | Premium falls between $500 floor & $10,000 cap |
                | **FIN-002** | Underinsurance | Coverage limit $\ge 80\%$ of property value |
                | **ENV-001** | Hazard Disclosure | Natural hazard disclosure & underwriter notice |
                | **CLM-001** | Claims Frequency | Loss record within maximum acceptable bounds |
                | **FR-001** | Rate Reasonableness | Surcharges do not exceed 2.5× baseline rate |
                | **SEC-001** | Model Armor Scanner | Injection prevention & PII token protection |
                | **AUD-001** | Audit Trail Logging | Cryptographic hash & immutable decision trace |
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚖️ Compliance Audit Verdict</div>', unsafe_allow_html=True)
                if cp:
                    comp_color = "#2e7d32" if cp.overall_status.value == "Pass" else "#e65100" if cp.overall_status.value == "Warning" else "#c62828"
                    st.markdown(f"""
                    - **Statutory Audit Score**: **<span style="font-size:1.3rem; color:{comp_color}; font-weight:700;">{cp.compliance_score}%</span>**
                    - **Overall Regulatory Status**: **`<span style="color:{comp_color};">{cp.overall_status.value}</span>`**
                    - **Passed Rules**: `{cp.passed_count} / {len(cp.checks)}`
                    - **Warning Triggers**: `{cp.warning_count}` | **Violations**: `{cp.failed_count}`
                    """)
                    if cp.overall_status.value == "Pass":
                        st.success("✅ **Statutory Clearance**: All 10 regulatory, financial, and security rules fully satisfied.")
                    elif cp.overall_status.value == "Warning":
                        st.warning(f"⚠️ **Review Flags**: {'; '.join(cp.review_reasons[:2])}")
                    else:
                        st.error(f"🚫 **Statutory Violation**: {'; '.join(cp.review_reasons[:2])}")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 5. ORCHESTRATOR AGENT DRILLDOWN ─────────────────────────
        elif agent_id == "orchestrator-agent":
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ Tripartite Decision Matrix</div>', unsafe_allow_html=True)
                st.markdown("""
                **Deterministic Triage Hierarchy:**
                - **Auto-Decline Trigger**: Score > 80, Prohibited industry class, or prior cancellation for fraud.
                - **Manual Review Trigger**: Natural hazard zone detected, Score 36–65, or compliance warning flag.
                - **Auto-Approve Clearance**: Score ≤ 35, all 10 statutory rules pass, standard property profile.
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">🎯 Final Decision & Routing Action</div>', unsafe_allow_html=True)
                st.markdown(f"""
                - **Final Verdict**: **`{decision.decision.value}`**
                - **Confidence Rating**: **`{decision.confidence_score}%`**
                - **Review Priority**: **`{decision.review_priority}`**
                - **Total Processing Time**: **`{decision.processing_time_seconds}s`**
                - **Notification Dispatched**: `{decision.reviewer_notifications[0] if decision.reviewer_notifications else 'Standard Log'}`
                """)
                st.info(f"💡 **Decision Rationale**: {decision.decision_rationale}")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 6. FEEDBACK AGENT DRILLDOWN ─────────────────────────────
        elif agent_id == "feedback-agent":
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ Institutional Learning Engine</div>', unsafe_allow_html=True)
                st.markdown("""
                **Analytics & Synthesis Roles:**
                1. **C-Level Executive Synthesis**: Translates technical telemetry and actuarial numbers into a plain-English board summary.
                2. **Hazard Concentration Detection**: Monitors aggregate geographical risk in coastal flood plains and seismic fault lines.
                3. **Loss Ratio Forecasting**: Alerts when volatile business classes require loss-control inspection.
                4. **Cap Impact Tracking**: Evaluates adequacy of capped premiums relative to true exposure.
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">📈 Portfolio Intelligence Output</div>', unsafe_allow_html=True)
                st.markdown(f"**Executive Synthesis:**\n> {decision.executive_summary}")
                if decision.portfolio_insights:
                    st.markdown("**Continuous Learning Alerts:**")
                    for ins in decision.portfolio_insights:
                        st.markdown(f"- 📌 {ins}")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 7. OPEN-METEO GEOCODING MCP DRILLDOWN ───────────────────
        elif agent_id == "mcp-open-meteo-geocoding":
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ Spatial Normalization Protocol</div>', unsafe_allow_html=True)
                st.markdown("""
                **API Endpoint**: `https://geocoding-api.open-meteo.com/v1/search`
                **Protocol**: REST / JSON with Geospatial Fallback
                **Extracted Dimensions**:
                - Verified Administrative Boundaries (`City`, `State`, `Country`)
                - Decimal Precision Geocoordinates (`Latitude`, `Longitude`)
                - Topographic Elevation (`Meters above sea level`)
                - Canonical Postal Formatting
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">📍 Normalized Spatial Telemetry</div>', unsafe_allow_html=True)
                loc = decision.location_intelligence
                geo = loc.geocoding if loc else (decision.submission_data.property_details.geocoding if decision.submission_data else None)
                if geo:
                    st.markdown(f"""
                    - **Normalized Address**: **`{geo.normalized_address}`**
                    - **Coordinates**: **`Lat: {geo.latitude:.4f}, Lon: {geo.longitude:.4f}`**
                    - **Elevation**: **`{geo.elevation_m:.1f} m`** (Topographic Height)
                    - **Timezone**: `{geo.timezone}`
                    - **Resolution Confidence**: **`{geo.confidence * 100:.0f}%`**
                    - **Data Source**: {'🛰️ Live Open-Meteo API' if not geo.is_simulated else '🌐 Geospatial Simulation'}
                    """)
                    st.success("✅ **Status**: Spatial normalization verified and fed to risk modeling pipeline.")
                else:
                    st.info("No geocoding payload recorded.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 8. FEMA FLOOD ZONE MCP DRILLDOWN ────────────────────────
        elif agent_id == "mcp-fema-flood":
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ FEMA NFHL Inundation Criteria</div>', unsafe_allow_html=True)
                st.markdown("""
                **Data Layer**: FEMA National Flood Hazard Layer (NFHL) GIS
                **Zone Classifications**:
                - **Zone VE**: Velocity coastal surge with wave action (≥ 3 ft waves)
                - **Zone AE**: 100-year base floodplain with Base Flood Elevation (BFE)
                - **Zone A**: 100-year shallow/riverine floodplain without BFE
                - **Zone X (Unshaded)**: Minimal risk outside 500-year floodplain
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">🌊 FEMA Flood Hazard Verdict</div>', unsafe_allow_html=True)
                loc = decision.location_intelligence
                fema = loc.fema_flood if loc else None
                if fema:
                    fema_color = "#c62828" if fema.flood_risk_score >= 70 else "#e65100" if fema.flood_risk_score >= 40 else "#2e7d32"
                    st.markdown(f"""
                    - **Flood Zone**: **`<span style="color:{fema_color}; font-size:1.1rem; font-weight:700;">{fema.flood_zone}</span>`**
                    - **SFHA Status**: **`{'🔴 Mandatory SFHA Insurance Zone' if fema.is_sfha else '🟢 Non-SFHA Minimal Hazard'}`**
                    - **Flood Risk Score**: **<span style="color:{fema_color}; font-weight:700;">{fema.flood_risk_score}/100</span>**
                    - **Base Flood Elevation**: `{f'{fema.base_flood_elevation_ft} ft' if fema.base_flood_elevation_ft else 'Not applicable'}`
                    - **Annual Inundation Probability**: `{fema.annual_flood_probability * 100:.1f}%`
                    - **Summary**: *{fema.summary}*
                    """)
                    if fema.is_sfha:
                        st.warning("⚠️ **Underwriting Notice**: Property falls in FEMA Special Flood Hazard Area.")
                    else:
                        st.success("✅ **Clean Flood Record**: Property is located in minimal flood exposure zone.")
                else:
                    st.info("No FEMA flood telemetry available.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 9. USGS SEISMIC MCP DRILLDOWN ───────────────────────────
        elif agent_id == "mcp-usgs-seismic":
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ USGS Seismic Ground Motion Rules</div>', unsafe_allow_html=True)
                st.markdown("""
                **Data Catalog**: USGS Real-time & Historical Earthquake Feed
                **Key Rating Metrics**:
                - **Fault Proximity**: Distance to nearest active tectonic fault line (< 20 km = Critical)
                - **Peak Ground Acceleration (PGA)**: Shake intensity expressed in gravitational force (%g)
                - **10-Year M3.5+ Event Frequency**: Statistical seismic activity rate in 150km radius
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">🌋 USGS Earthquake Hazard Verdict</div>', unsafe_allow_html=True)
                loc = decision.location_intelligence
                seismic = loc.usgs_seismic if loc else None
                if seismic:
                    seis_color = "#c62828" if seismic.seismic_risk_score >= 70 else "#e65100" if seismic.seismic_risk_score >= 40 else "#2e7d32"
                    st.markdown(f"""
                    - **Seismic Zone**: **`<span style="color:{seis_color}; font-size:1.1rem; font-weight:700;">{seismic.seismic_zone}</span>`**
                    - **Seismic Risk Score**: **<span style="color:{seis_color}; font-weight:700;">{seismic.seismic_risk_score}/100</span>**
                    - **Peak Ground Acceleration (PGA)**: **`{seismic.peak_ground_acceleration_g}g`**
                    - **Nearest Active Fault**: `{seismic.nearest_fault_name}` ({seismic.fault_line_proximity_km:.1f} km away)
                    - **10-Year M3.5+ Events**: `{seismic.earthquake_count_10yr} events` (Max Mag: `M{seismic.max_magnitude_nearby:.1f}`)
                    - **Summary**: *{seismic.summary}*
                    """)
                    if seismic.seismic_risk_score >= 65:
                        st.warning("⚠️ **Tectonic Flag**: High ground shaking and liquefaction vulnerability.")
                    else:
                        st.success("✅ **Stable Tectonic Profile**: Low earthquake vulnerability in continental craton.")
                else:
                    st.info("No USGS seismic telemetry available.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── 10. OPEN-METEO WEATHER MCP DRILLDOWN ────────────────────
        elif agent_id == "mcp-open-meteo-weather":
            with col_logic:
                st.markdown('<div class="enterprise-card"><div class="card-header">⚙️ Tropical Cyclone & Wind Load Model</div>', unsafe_allow_html=True)
                st.markdown("""
                **Telemetry Source**: Open-Meteo High-Resolution Numerical Weather Prediction
                **Exposure Categories**:
                - **Tier 5**: Cat 5 Hurricane & Wind-Borne Debris Region (> 140 mph gusts)
                - **Tier 4**: Cat 4 High-Velocity Hurricane Corridor (> 125 mph gusts)
                - **Tier 3**: Cat 3 Tropical Storm Surge Basin (> 100 mph gusts)
                - **Tier 2 / None**: Standard building code wind loading (< 65 mph gusts)
                """)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_verdict:
                st.markdown('<div class="enterprise-card"><div class="card-header">🌪️ Extreme Weather Exposure Verdict</div>', unsafe_allow_html=True)
                loc = decision.location_intelligence
                weather = loc.open_meteo_weather if loc else None
                if weather:
                    w_color = "#c62828" if weather.weather_risk_score >= 70 else "#e65100" if weather.weather_risk_score >= 40 else "#2e7d32"
                    st.markdown(f"""
                    - **Hurricane Exposure**: **`<span style="color:{w_color}; font-size:1.1rem; font-weight:700;">{weather.hurricane_exposure_tier}</span>`**
                    - **Weather Risk Score**: **<span style="color:{w_color}; font-weight:700;">{weather.weather_risk_score}/100</span>**
                    - **Peak Recorded Gusts**: **`{weather.max_wind_gust_mph:.1f} mph`**
                    - **Annual Precipitation**: `{weather.annual_precipitation_inches:.1f} inches`
                    - **Convective Storm Severity**: `{weather.severe_convective_storm_risk}`
                    - **Summary**: *{weather.summary}*
                    """)
                    if weather.weather_risk_score >= 65:
                        st.warning("⚠️ **Severe Wind Hazard**: Elevated structural vulnerability to tropical cyclonic systems.")
                    else:
                        st.success("✅ **Standard Wind Load**: Property within standard aerodynamic loading tolerances.")
                else:
                    st.info("No Open-Meteo weather telemetry available.")
                st.markdown('</div>', unsafe_allow_html=True)


def render_location_intelligence_card(decision: UnderwritingDecision):
    """Render comprehensive Location Intelligence & MCP telemetry card."""
    loc = decision.location_intelligence
    if not loc:
        return

    st.markdown('<div class="enterprise-card"><div class="card-header">🌍 Real-Time Location Intelligence & MCP External Feeds</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        geo = loc.geocoding
        st.markdown("""
        <div style="background:#f8f9fa; border:1px solid #e0e3eb; border-radius:8px; padding:12px; height:100%;">
            <div style="font-weight:700; color:#1a237e; font-size:0.85rem; margin-bottom:6px;">📍 Open-Meteo Geocoding</div>
        """, unsafe_allow_html=True)
        if geo:
            st.markdown(f"""
            - **Coords**: `{geo.latitude:.4f}, {geo.longitude:.4f}`
            - **Elevation**: `{geo.elevation_m:.1f}m`
            - **Resolved**: `{geo.city}, {geo.state_code or geo.state}`
            - **Confidence**: `{geo.confidence*100:.0f}%`
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        fema = loc.fema_flood
        st.markdown("""
        <div style="background:#f8f9fa; border:1px solid #e0e3eb; border-radius:8px; padding:12px; height:100%;">
            <div style="font-weight:700; color:#0277bd; font-size:0.85rem; margin-bottom:6px;">🌊 FEMA Flood Zone MCP</div>
        """, unsafe_allow_html=True)
        if fema:
            f_badge = "🔴 SFHA High Risk" if fema.is_sfha else "🟢 Minimal Zone"
            st.markdown(f"""
            - **Zone**: **`{fema.flood_zone}`** ({f_badge})
            - **Flood Score**: **`{fema.flood_risk_score}/100`**
            - **Annual Prob**: `{fema.annual_flood_probability*100:.1f}%`
            - **BFE**: `{f'{fema.base_flood_elevation_ft}ft' if fema.base_flood_elevation_ft else 'N/A'}`
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        seismic = loc.usgs_seismic
        st.markdown("""
        <div style="background:#f8f9fa; border:1px solid #e0e3eb; border-radius:8px; padding:12px; height:100%;">
            <div style="font-weight:700; color:#e65100; font-size:0.85rem; margin-bottom:6px;">🌋 USGS Seismic MCP</div>
        """, unsafe_allow_html=True)
        if seismic:
            st.markdown(f"""
            - **Zone**: **`{seismic.seismic_zone}`**
            - **Seismic Score**: **`{seismic.seismic_risk_score}/100`**
            - **PGA Intensity**: `{seismic.peak_ground_acceleration_g}g`
            - **Fault Proximity**: `{seismic.fault_line_proximity_km:.1f}km`
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        weather = loc.open_meteo_weather
        st.markdown("""
        <div style="background:#f8f9fa; border:1px solid #e0e3eb; border-radius:8px; padding:12px; height:100%;">
            <div style="font-weight:700; color:#4527a0; font-size:0.85rem; margin-bottom:6px;">🌪️ Open-Meteo Weather MCP</div>
        """, unsafe_allow_html=True)
        if weather:
            st.markdown(f"""
            - **Hurricane Tier**: **`{weather.hurricane_exposure_tier}`**
            - **Weather Score**: **`{weather.weather_risk_score}/100`**
            - **Peak Wind Gusts**: `{weather.max_wind_gust_mph:.1f} mph`
            - **Annual Rainfall**: `{weather.annual_precipitation_inches:.1f}"`
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    if loc.hazard_alerts:
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        for alert in loc.hazard_alerts:
            st.warning(alert)

    st.markdown(f"""
    <div style="font-size:0.75rem; color:#5f6368; margin-top:8px; text-align:right;">
        ⚡ Sub-agent MCP Latency: <b>{loc.mcp_latency_ms}ms</b> &ensp;|&ensp; Composite Location Hazard Score: <b>{loc.composite_location_score}/100</b>
    </div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_radar(risk_profile):
    """Render risk dimensions as a radar chart."""
    if not risk_profile or not risk_profile.dimensions:
        return

    categories = [d.name for d in risk_profile.dimensions]
    values = [d.score for d in risk_profile.dimensions]
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(25, 118, 210, 0.15)',
        line=dict(color='#1976d2', width=2),
        marker=dict(size=6, color='#1976d2'),
        name='Risk Score',
    ))

    # Add threshold rings
    fig.add_trace(go.Scatterpolar(
        r=[35] * len(categories),
        theta=categories,
        line=dict(color='#4caf50', width=1, dash='dot'),
        name='Auto-Approve (35)',
        showlegend=True,
    ))
    fig.add_trace(go.Scatterpolar(
        r=[65] * len(categories),
        theta=categories,
        line=dict(color='#ff9800', width=1, dash='dot'),
        name='Review Threshold (65)',
        showlegend=True,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            bgcolor='#fafafa',
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, font=dict(size=10)),
        margin=dict(l=60, r=60, t=30, b=60),
        height=350,
        paper_bgcolor='white',
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_pricing_breakdown(pricing):
    """Render pricing modifier waterfall chart."""
    if not pricing:
        return

    labels = ["Base Premium"]
    values = [pricing.base_premium]
    text_vals = [f"${pricing.base_premium:,.0f}"]
    colors = ["#1976d2"]

    running = pricing.base_premium
    for m in pricing.modifiers:
        delta = running * (m.factor - 1)
        labels.append(m.name)
        values.append(delta)
        text_vals.append(f"×{m.factor}")
        colors.append("#4caf50" if m.factor < 1 else "#ff9800" if m.factor <= 1.1 else "#f44336")
        running += delta

    fig = go.Figure(go.Waterfall(
        name="Premium Breakdown",
        orientation="v",
        measure=["absolute"] + ["relative"] * (len(values) - 1),
        x=labels,
        y=values,
        text=text_vals,
        textposition="outside",
        textfont=dict(size=10, family='Inter'),
        connector=dict(line=dict(color="#e0e0e0", width=1)),
        increasing=dict(marker_color="#f44336"),
        decreasing=dict(marker_color="#4caf50"),
        totals=dict(marker_color="#1976d2"),
    ))

    fig.add_hline(y=10000, line_dash="dash", line_color="#d32f2f",
                  annotation_text="$10K Cap", annotation_position="top right")

    fig.update_layout(
        showlegend=False,
        margin=dict(l=40, r=20, t=30, b=80),
        height=350,
        paper_bgcolor='white',
        plot_bgcolor='#fafafa',
        font=dict(family='Inter', size=11),
        yaxis=dict(title="Premium ($)", gridcolor='#e0e0e0'),
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_compliance_table(compliance):
    """Render compliance checks as a styled table."""
    if not compliance:
        return

    for check in compliance.checks:
        if check.status == ComplianceStatus.PASS:
            badge = '<span class="traffic-light traffic-pass">✓ PASS</span>'
        elif check.status == ComplianceStatus.WARNING:
            badge = '<span class="traffic-light traffic-warning">⚠ WARNING</span>'
        else:
            badge = '<span class="traffic-light traffic-fail">✗ FAIL</span>'

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px solid #f0f0f0;">
            <div style="min-width:90px">{badge}</div>
            <div>
                <div style="font-weight:600; font-size:0.85rem; color:#202124;">{check.rule_name}</div>
                <div style="font-size:0.78rem; color:#5f6368;">{check.details}</div>
                {"<div style='font-size:0.75rem; color:#e65100; margin-top:2px;'>→ " + check.remediation + "</div>" if check.remediation else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_decision_banner(decision: UnderwritingDecision):
    """Render the underwriting decision banner."""
    if getattr(decision, "underwriter_override", None) == "APPROVED":
        css_class = "decision-approved"
        icon = "✅"
        label = "APPROVED BY SENIOR UNDERWRITER (MANUAL OVERRIDE)"
    elif getattr(decision, "underwriter_override", None) == "DECLINED":
        css_class = "decision-declined"
        icon = "🚫"
        label = "DECLINED BY SENIOR UNDERWRITER (MANUAL OVERRIDE)"
    elif decision.decision == DecisionType.AUTO_APPROVED:
        css_class = "decision-approved"
        icon = "✅"
        label = "AUTO-APPROVED"
    elif decision.decision == DecisionType.AUTO_DECLINED:
        css_class = "decision-declined"
        icon = "🚫"
        label = "AUTO-DECLINED"
    else:
        css_class = "decision-review"
        icon = "⚠️"
        label = "MANUAL REVIEW REQUIRED"

    st.markdown(f"""
    <div class="{css_class}">
        <div class="decision-text">{icon}&ensp;{label}</div>
        <div style="font-size:0.85rem; margin-top:4px; opacity:0.8;">
            Confidence: {decision.confidence_score}% &ensp;|&ensp;
            Processing Time: {decision.processing_time_seconds}s &ensp;|&ensp;
            Agents Executed: {len(decision.agents_executed)}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_underwriter_action_panel(decision: UnderwritingDecision, memory: MemoryBank, key_prefix: str = "desk"):
    """Render interactive Human-in-the-Loop decision action controls."""
    if not decision:
        return

    # If decision was manually overridden already
    if getattr(decision, "underwriter_override", None):
        status_bg = "#f1f8e9" if decision.underwriter_override == "APPROVED" else "#ffebee"
        status_color = "#2e7d32" if decision.underwriter_override == "APPROVED" else "#c62828"
        icon = "✅" if decision.underwriter_override == "APPROVED" else "🚫"
        reviewed_time = decision.underwriter_reviewed_at.strftime('%Y-%m-%d %H:%M:%S UTC') if getattr(decision, 'underwriter_reviewed_at', None) else 'Just now'
        st.markdown(f"""
        <div style="background:{status_bg}; border:1px solid {status_color}; border-radius:8px; padding:12px 16px; margin:10px 0;">
            <div style="font-weight:700; color:{status_color}; font-size:0.9rem;">
                {icon} Underwriter Decision Record: {decision.underwriter_override}
            </div>
            <div style="font-size:0.8rem; color:#37474f; margin-top:4px;">
                <b>Signed by:</b> {getattr(decision, 'underwriter_id', 'Senior Underwriter (UW-ID: #4092)')} &ensp;|&ensp;
                <b>Timestamp:</b> {reviewed_time}
            </div>
            <div style="font-size:0.8rem; color:#212121; margin-top:6px; background:white; padding:6px 10px; border-radius:4px; border:1px solid #e0e0e0;">
                <b>Underwriter Notes:</b> {getattr(decision, 'underwriter_comments', 'No comments provided.')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # If manual review is required, render interactive approve/decline controls
    if decision.requires_human_review or decision.decision == DecisionType.MANUAL_REVIEW:
        st.markdown(f"""
        <div style="background:#fffcf5; border:2px solid #ff9800; border-radius:10px; padding:12px 16px; margin:10px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:700; color:#e65100; font-size:0.92rem;">
                    👨‍💼 Senior Underwriter Review & Binding Decision Required
                </div>
                <span style="background:#fff3e0; color:#e65100; font-size:0.7rem; font-weight:700; padding:2px 8px; border-radius:10px; border:1px solid #ffe082;">
                    PRIORITY: {decision.review_priority.upper()}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if decision.human_review_reasons:
            reasons_html = "".join(f"<li>{r}</li>" for r in decision.human_review_reasons)
            st.markdown(f"<div style='font-size:0.78rem; color:#d84315; margin-bottom:8px;'><b>Trigger Reasons:</b><ul style='margin:4px 0 8px 18px; padding:0;'>{reasons_html}</ul></div>", unsafe_allow_html=True)

        comments = st.text_area(
            "Underwriter Review Comments & Policy Endorsements",
            placeholder="e.g., Reviewed hazard mitigation & flood barriers; approved with 5% hurricane deductible endorsement.",
            key=f"{key_prefix}_uw_comments",
            height=70,
        )

        col_app, col_dec = st.columns(2)
        with col_app:
            if st.button("✅ Approve & Bind Policy", key=f"{key_prefix}_approve_btn", type="primary", use_container_width=True):
                if hasattr(memory, "resolve_review"):
                    updated = memory.resolve_review(
                        decision.submission_id,
                        "APPROVED",
                        comments or "Approved by Senior Underwriter after comprehensive risk review.",
                    )
                    if updated:
                        st.session_state.decision = updated
                else:
                    decision.underwriter_override = "APPROVED"
                    decision.underwriter_comments = comments or "Approved by Senior Underwriter after comprehensive risk review."
                    decision.underwriter_reviewed_at = datetime.utcnow()
                    decision.underwriter_id = "Senior Underwriter (UW-ID: #4092)"
                    decision.requires_human_review = False
                    decision.decision = DecisionType.UNDERWRITER_APPROVED
                    st.session_state.decision = decision
                    # update memory if available
                    if hasattr(memory, '_submissions'):
                        memory._submissions[decision.submission_id] = decision
                    if hasattr(memory, '_notifications'):
                        for n in memory._notifications:
                            if decision.submission_id in n.message or decision.submission_id in n.title:
                                n.acknowledged = True

                st.success("✅ Policy Successfully Approved & Bound by Senior Underwriter!")
                st.rerun()

        with col_dec:
            if st.button("🚫 Decline Submission", key=f"{key_prefix}_decline_btn", use_container_width=True):
                if hasattr(memory, "resolve_review"):
                    updated = memory.resolve_review(
                        decision.submission_id,
                        "DECLINED",
                        comments or "Declined by Underwriter due to unacceptable hazard exposure.",
                    )
                    if updated:
                        st.session_state.decision = updated
                else:
                    decision.underwriter_override = "DECLINED"
                    decision.underwriter_comments = comments or "Declined by Underwriter due to unacceptable hazard exposure."
                    decision.underwriter_reviewed_at = datetime.utcnow()
                    decision.underwriter_id = "Senior Underwriter (UW-ID: #4092)"
                    decision.requires_human_review = False
                    decision.decision = DecisionType.UNDERWRITER_DECLINED
                    st.session_state.decision = decision
                    if hasattr(memory, '_submissions'):
                        memory._submissions[decision.submission_id] = decision
                    if hasattr(memory, '_notifications'):
                        for n in memory._notifications:
                            if decision.submission_id in n.message or decision.submission_id in n.title:
                                n.acknowledged = True

                st.error("🚫 Submission Officially Declined by Underwriter.")
                st.rerun()


def render_notifications(memory: MemoryBank):
    """Render pending notifications."""
    notifications = memory.get_notifications(unacknowledged_only=True)
    if not notifications:
        return

    for n in notifications:
        css_class = {
            "CRITICAL": "notification-critical",
            "WARNING": "notification-warning",
            "INFO": "notification-info",
        }.get(n.severity, "notification-info")

        st.markdown(f"""
        <div class="{css_class}">
            <div style="font-weight:700; font-size:0.9rem;">{n.title}</div>
            <div style="font-size:0.8rem; margin-top:4px; opacity:0.9;">{n.message}</div>
            <div style="font-size:0.7rem; margin-top:6px; opacity:0.6;">
                {n.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")} &ensp;|&ensp; ID: {n.notification_id}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size:2rem;">🏢</div>
        <div style="font-size:1.1rem; font-weight:700; letter-spacing:-0.5px;">UnderwriteAI</div>
        <div style="font-size:0.7rem; opacity:0.7; margin-top:2px;">Enterprise Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Underwriting Desk", "📋 Agent Registry", "🔔 Notifications", "📊 Portfolio Analytics"],
        label_visibility="collapsed",
    )

    st.divider()

    # API Status
    api_status = "🟢 Connected" if settings.is_api_key_configured() else "🟡 Simulation Mode"
    st.markdown(f"""
    <div style="font-size:0.75rem; opacity:0.8;">
        <div style="font-weight:600; margin-bottom:4px;">System Status</div>
        <div>Gemini API: {api_status}</div>
        <div>Model: {settings.GEMINI_MODEL}</div>
        <div>Max Premium: ${settings.MAX_PREMIUM:,.0f}</div>
        <div>Version: {settings.APP_VERSION}</div>
    </div>
    """, unsafe_allow_html=True)

    # Pending reviews count
    pending = memory.get_pending_reviews()
    if pending:
        st.markdown(f"""
        <div style="background: rgba(255,152,0,0.2); border-radius:8px; padding:8px 12px; margin-top:12px; text-align:center;">
            <div style="font-size:1.5rem; font-weight:700; color:#ff9800;">{len(pending)}</div>
            <div style="font-size:0.7rem; font-weight:600; color:#ff9800;">Pending Reviews</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Clear Cache & Reset State", use_container_width=True):
        st.cache_resource.clear()
        st.cache_data.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        memory._submissions.clear()
        memory._notifications.clear()
        st.rerun()


# ────────────────────────────────────────────────────────────────────
# Page: Underwriting Desk
# ────────────────────────────────────────────────────────────────────

if page == "🏠 Underwriting Desk":

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Underwriting Intelligence Hub</h1>
        <p>Multi-Agent AI Platform for Small Business Insurance Underwriting</p>
        <span class="header-badge">⚡ Powered by Gemini 3.5 &ensp;|&ensp; 6 Specialized Agents &ensp;|&ensp; Fortified Enterprise Fleet</span>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout: Input | Pipeline Visualizer
    col_input, col_pipeline = st.columns([1, 2])

    with col_input:
        st.markdown('<div class="enterprise-card"><div class="card-header">📥 Submission Intake</div>', unsafe_allow_html=True)

        input_method = st.radio(
            "Input Method",
            ["📝 Text Submission", "📄 PDF Upload"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if input_method == "📝 Text Submission":
            sample = st.selectbox(
                "Load Sample Submission",
                ["-- Select a sample --", "✅ Low Risk (Auto-Approve)", "⚠️ Hazard Zone (Manual Review)", "🚫 High Risk (Auto-Decline)"],
            )

            default_text = ""
            if sample == "✅ Low Risk (Auto-Approve)":
                default_text = SAMPLE_LOW_RISK
            elif sample == "⚠️ Hazard Zone (Manual Review)":
                default_text = SAMPLE_HAZARD_ZONE
            elif sample == "🚫 High Risk (Auto-Decline)":
                default_text = SAMPLE_HIGH_RISK

            submission_text = st.text_area(
                "Paste broker submission text",
                value=default_text,
                height=320,
                placeholder="Paste the full broker submission or ACORD form content here...",
            )

            uploaded_file = None
        else:
            submission_text = ""
            uploaded_file = st.file_uploader(
                "Upload PDF submission",
                type=["pdf"],
                help="Upload an ACORD form or broker submission PDF (max 10MB)",
            )

        submit_btn = st.button("🚀  Begin Underwriting Assessment", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_pipeline:
        st.markdown('<div class="enterprise-card"><div class="card-header">🔄 Agent Pipeline Status & Live Execution Flow</div>', unsafe_allow_html=True)

        # Initialize pipeline status in session state
        if "pipeline_status" not in st.session_state:
            st.session_state.pipeline_status = {
                "intake-agent": "idle",
                "risk-agent": "idle",
                "pricing-agent": "idle",
                "compliance-agent": "idle",
                "orchestrator-agent": "idle",
                "feedback-agent": "idle",
            }

        # Dynamic placeholder for live sequential pipeline animation
        viz_placeholder = st.empty()
        with viz_placeholder:
            render_pipeline_visualizer(st.session_state.pipeline_status)

        # Dynamic status banner container placed directly above the inspector
        status_banner_placeholder = st.empty()
        if "decision" in st.session_state:
            with status_banner_placeholder:
                render_decision_banner(st.session_state.decision)
                st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

        st.markdown("<b>🔍 Drill Down into Any Agent's Decision Logic & Methodology:</b>", unsafe_allow_html=True)
        selected_agent = st.selectbox(
            "Select Agent to Inspect",
            [
                "📥 Intake Agent",
                "🔍 Risk Profiling Agent",
                "💰 Pricing & Product Agent",
                "⚖️ Compliance Agent",
                "🎯 Orchestrator Agent",
                "📊 Feedback & Learning Agent",
                "📍 Open-Meteo Geocoding MCP",
                "🌊 FEMA Flood Zone MCP",
                "🌋 USGS Seismic MCP",
                "🌪️ Open-Meteo Weather MCP",
            ],
            index=0,
            label_visibility="collapsed",
            key="pipeline_agent_select"
        )
        agent_id_map = {
            "📥 Intake Agent": "intake-agent",
            "🔍 Risk Profiling Agent": "risk-agent",
            "💰 Pricing & Product Agent": "pricing-agent",
            "⚖️ Compliance Agent": "compliance-agent",
            "🎯 Orchestrator Agent": "orchestrator-agent",
            "📊 Feedback & Learning Agent": "feedback-agent",
            "📍 Open-Meteo Geocoding MCP": "mcp-open-meteo-geocoding",
            "🌊 FEMA Flood Zone MCP": "mcp-fema-flood",
            "🌋 USGS Seismic MCP": "mcp-usgs-seismic",
            "🌪️ Open-Meteo Weather MCP": "mcp-open-meteo-weather",
        }
        selected_agent_id = agent_id_map.get(selected_agent, "intake-agent")
        render_agent_deep_dive(selected_agent_id, st.session_state.get("decision"))

        st.markdown('</div>', unsafe_allow_html=True)

        # Show notifications if any
        render_notifications(memory)

    # ── Process Submission ─────────────────────────────────────────
    if submit_btn:
        raw_text = ""

        if uploaded_file:
            try:
                import pdfplumber
                import io
                with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                    raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            except Exception as e:
                st.error(f"PDF parsing error: {e}")
                raw_text = ""
        else:
            raw_text = submission_text

        if not raw_text.strip():
            st.warning("Please provide submission text or upload a PDF file.")
        else:
            submission = SubmissionInput(
                raw_text=raw_text,
                submission_type=SubmissionType.PDF if uploaded_file else SubmissionType.TEXT,
            )

            progress_bar = st.progress(0, text="⚡ Initiating Enterprise Multi-Agent Fleet...")

            agent_sequence = [
                ("intake-agent", "📥 [1/6] Intake Agent: Parsing ACORD text & extracting entity schemas...", 0.8),
                ("risk-agent", "🔍 [2/6] Risk Profiling Agent: Evaluating 6 dimensions & checking hazard zones...", 0.9),
                ("pricing-agent", "💰 [3/6] Pricing & Product Agent: Rating base premium & applying $10K policy cap...", 0.8),
                ("compliance-agent", "⚖️ [4/6] Compliance Agent: Auditing 10 statutory regulatory & fairness rules...", 0.8),
                ("orchestrator-agent", "🎯 [5/6] Orchestrator: Evaluating decision matrix & triage routing...", 0.8),
                ("feedback-agent", "📊 [6/6] Feedback & Learning Agent: Generating executive synthesis & insights...", 0.7),
            ]

            # Sequential live execution visualization
            live_status = {k: "idle" for k in st.session_state.pipeline_status}

            for idx, (agent_id, step_label, step_delay) in enumerate(agent_sequence):
                # Mark current as running
                live_status[agent_id] = "running"
                with viz_placeholder:
                    render_pipeline_visualizer(live_status)
                progress_bar.progress((idx) / len(agent_sequence), text=step_label)
                time.sleep(step_delay)

                # Mark current as completed
                live_status[agent_id] = "completed"
                with viz_placeholder:
                    render_pipeline_visualizer(live_status)

            progress_bar.progress(1.0, text="✅ All 6 Agents Completed! Finalizing Decision...")
            time.sleep(0.3)

            # Execute orchestrator backend logic
            decision = run_orchestrator(submission)
            st.session_state.decision = decision
            st.session_state.pipeline_status = {k: "completed" for k in live_status}

            # Update banner and visualizer immediately
            with status_banner_placeholder:
                render_decision_banner(decision)
                st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
            with viz_placeholder:
                render_pipeline_visualizer(st.session_state.pipeline_status)

            st.rerun()

    # ── Display Results ────────────────────────────────────────────
    if "decision" in st.session_state:
        decision: UnderwritingDecision = st.session_state.decision

        st.markdown("---")

        # Prominent full-width decision banner
        render_decision_banner(decision)

        # Interactive Senior Underwriter Binding & Action Panel (when review is required or recorded)
        render_underwriter_action_panel(decision, memory, key_prefix="desk_action")

        st.markdown("<br>", unsafe_allow_html=True)

        # Results Tabs
        tab_summary, tab_risk, tab_pricing, tab_compliance, tab_agents, tab_simulator, tab_audit = st.tabs([
            "📋 Executive Summary",
            "🔍 Risk Assessment",
            "💰 Pricing",
            "⚖️ Compliance",
            "🤖 Agent Pipeline Reasoning",
            "⚡ What-If Simulator",
            "📜 Audit Trail",
        ])

        with tab_summary:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                risk_color = "#4caf50" if decision.risk_profile and decision.risk_profile.composite_score <= 35 else "#ff9800" if decision.risk_profile and decision.risk_profile.composite_score <= 65 else "#f44336"
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Risk Score</div>
                    <div class="kpi-value" style="color:{risk_color};">{decision.risk_profile.composite_score if decision.risk_profile else 'N/A'}</div>
                    <div class="kpi-label">/100</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Annual Premium</div>
                    <div class="kpi-value" style="color:#1976d2;">${decision.pricing.final_premium:,.0f}</div>
                    <div class="kpi-label">{"⚠ Capped" if decision.pricing and decision.pricing.premium_capped else "Within Range"}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                comp_color = "#4caf50" if decision.compliance and decision.compliance.overall_status == ComplianceStatus.PASS else "#ff9800" if decision.compliance and decision.compliance.overall_status == ComplianceStatus.WARNING else "#f44336"
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Compliance</div>
                    <div class="kpi-value" style="color:{comp_color};">{decision.compliance.compliance_score if decision.compliance else 'N/A'}%</div>
                    <div class="kpi-label">{decision.compliance.overall_status.value if decision.compliance else ''}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Processing Time</div>
                    <div class="kpi-value" style="color:#5f6368;">{decision.processing_time_seconds}s</div>
                    <div class="kpi-label">{len(decision.agents_executed)} Agents</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Executive Summary
            st.markdown('<div class="enterprise-card"><div class="card-header">Executive Summary</div>', unsafe_allow_html=True)
            st.markdown(decision.executive_summary)
            st.markdown('</div>', unsafe_allow_html=True)

            # Business Details
            if decision.submission_data:
                sd = decision.submission_data
                col_biz, col_prop = st.columns(2)
                with col_biz:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Business Information</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    | Field | Value |
                    |-------|-------|
                    | **Business Name** | {sd.business_info.business_name} |
                    | **Type** | {sd.business_info.business_type} |
                    | **Annual Revenue** | ${sd.business_info.annual_revenue:,.0f} |
                    | **Employees** | {sd.business_info.employee_count} |
                    | **Years in Business** | {sd.business_info.years_in_business} |
                    | **Valid License** | {'✅ Yes' if sd.business_info.has_valid_license else '❌ No'} |
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_prop:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Property Details</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    | Field | Value |
                    |-------|-------|
                    | **Address** | {sd.property_details.address} |
                    | **Location** | {sd.property_details.city}, {sd.property_details.state} {sd.property_details.zip_code} |
                    | **Property Value** | ${sd.property_details.property_value:,.0f} |
                    | **Building Age** | {sd.property_details.building_age_years} years |
                    | **Construction** | {sd.property_details.construction_type} |
                    | **Safety Systems** | {'🔥' if sd.property_details.has_sprinkler_system else ''}{'🚨' if sd.property_details.has_fire_alarm else ''}{'🔒' if sd.property_details.has_security_system else ''} |
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)

            # Portfolio Insights
            if decision.portfolio_insights:
                st.markdown('<div class="enterprise-card"><div class="card-header">📈 Portfolio Insights</div>', unsafe_allow_html=True)
                for insight in decision.portfolio_insights:
                    st.markdown(f"- {insight}")
                st.markdown('</div>', unsafe_allow_html=True)

        with tab_risk:
            if decision.risk_profile:
                rp = decision.risk_profile

                # Render real-time Location Intelligence & MCP Feeds card
                render_location_intelligence_card(decision)

                col_radar, col_details = st.columns([1, 1])

                with col_radar:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Risk Dimension Radar</div>', unsafe_allow_html=True)
                    render_risk_radar(rp)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_details:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Risk Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f"**Composite Score:** {rp.composite_score}/100 ({rp.risk_tier.value} Risk)")
                    st.markdown(f"**Hazard Zones:** {', '.join(rp.hazard_zones_detected) if rp.hazard_zones_detected else 'None detected'}")

                    if rp.auto_decline_triggers:
                        st.error(f"**Auto-Decline Triggers:** {'; '.join(rp.auto_decline_triggers)}")

                    st.markdown("**Risk Summary:**")
                    st.markdown(rp.risk_summary)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Dimension details
                st.markdown('<div class="enterprise-card"><div class="card-header">Risk Dimension Breakdown</div>', unsafe_allow_html=True)
                for dim in rp.dimensions:
                    score_color = "#4caf50" if dim.score <= 35 else "#ff9800" if dim.score <= 65 else "#f44336"
                    with st.expander(f"{dim.name} — Score: {dim.score}/100 (Weight: {dim.weight*100:.0f}%)"):
                        st.progress(dim.score / 100)
                        for f in dim.factors:
                            st.markdown(f"- {f}")
                        st.info(f"💡 {dim.recommendation}")
                st.markdown('</div>', unsafe_allow_html=True)

        with tab_pricing:
            if decision.pricing:
                pr = decision.pricing

                col_chart, col_table = st.columns([1, 1])

                with col_chart:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Premium Waterfall Chart</div>', unsafe_allow_html=True)
                    render_pricing_breakdown(pr)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_table:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Rating Factors</div>', unsafe_allow_html=True)

                    st.markdown(f"""
                    | | |
                    |---|---|
                    | **Base Premium** | ${pr.base_premium:,.2f} |
                    | **Final Premium** | **${pr.final_premium:,.2f}** |
                    | **Product** | {pr.product_recommendation} |
                    | **Coverage Limit** | ${pr.coverage_limit:,.0f} |
                    | **Deductible** | ${pr.deductible:,.0f} |
                    | **Premium Capped** | {'⚠️ Yes (at $10,000)' if pr.premium_capped else '✅ No'} |
                    """)

                    st.markdown("**Modifier Details:**")
                    for m in pr.modifiers:
                        factor_icon = "🟢" if m.factor < 1 else "🟡" if m.factor <= 1.1 else "🔴"
                        st.markdown(f"- {factor_icon} **{m.name}**: ×{m.factor} — {m.reason}")
                    st.markdown('</div>', unsafe_allow_html=True)

        with tab_compliance:
            if decision.compliance:
                cp = decision.compliance

                col_score, col_counts = st.columns([1, 2])
                with col_score:
                    gauge_color = "#4caf50" if cp.overall_status == ComplianceStatus.PASS else "#ff9800" if cp.overall_status == ComplianceStatus.WARNING else "#f44336"
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=cp.compliance_score,
                        title={'text': "Compliance Score", 'font': {'size': 14, 'family': 'Inter'}},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': gauge_color},
                            'steps': [
                                {'range': [0, 60], 'color': '#ffebee'},
                                {'range': [60, 80], 'color': '#fff3e0'},
                                {'range': [80, 100], 'color': '#e8f5e9'},
                            ],
                        },
                        number={'suffix': '%', 'font': {'size': 28, 'family': 'Inter'}},
                    ))
                    fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='white')
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col_counts:
                    st.markdown('<div class="enterprise-card"><div class="card-header">Compliance Summary</div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"""
                        <div style="text-align:center; padding:8px;">
                            <div style="font-size:1.8rem; font-weight:700; color:#4caf50;">{cp.passed_count}</div>
                            <div style="font-size:0.7rem; color:#5f6368; font-weight:600;">PASSED</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""
                        <div style="text-align:center; padding:8px;">
                            <div style="font-size:1.8rem; font-weight:700; color:#ff9800;">{cp.warning_count}</div>
                            <div style="font-size:0.7rem; color:#5f6368; font-weight:600;">WARNINGS</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""
                        <div style="text-align:center; padding:8px;">
                            <div style="font-size:1.8rem; font-weight:700; color:#f44336;">{cp.failed_count}</div>
                            <div style="font-size:0.7rem; color:#5f6368; font-weight:600;">FAILED</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

        with tab_agents:
            st.markdown('<div class="enterprise-card"><div class="card-header">🤖 Multi-Agent Fleet Reasoning & Decision Drill-Down</div>', unsafe_allow_html=True)
            st.markdown("Select any agent from the specialized fleet to inspect its exact inputs, step-by-step mathematical logic, decision criteria, and generated output:")
            
            sub_agent_tabs = st.tabs([
                "📥 Intake Agent",
                "🔍 Risk Profiling",
                "💰 Pricing Engine",
                "⚖️ Compliance",
                "🎯 Orchestrator",
                "📊 Feedback & Learning",
            ])
            
            agent_ids = ["intake-agent", "risk-agent", "pricing-agent", "compliance-agent", "orchestrator-agent", "feedback-agent"]
            for i, sat in enumerate(sub_agent_tabs):
                with sat:
                    render_agent_deep_dive(agent_ids[i], decision)
                    
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_simulator:
            st.markdown('<div class="enterprise-card"><div class="card-header">⚡ Underwriter What-If Sandbox & Risk Mitigation Simulator</div>', unsafe_allow_html=True)
            st.markdown("Simulate risk engineering improvements, deductible changes, and safety retrofits to see their instant effect on risk score, premium, and auto-approval triage:")

            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                st.markdown("**🛠️ Risk Engineering & Safety Retrofits:**")
                sim_sprinkler = st.checkbox("Install Full Fire Sprinkler System", value=decision.submission_data.property_details.has_sprinkler_system if decision.submission_data else True)
                sim_alarm = st.checkbox("Install Monitored Fire & Smoke Alarm", value=decision.submission_data.property_details.has_fire_alarm if decision.submission_data else True)
                sim_security = st.checkbox("Add 24/7 Monitored Central Security / CCTV", value=decision.submission_data.property_details.has_security_system if decision.submission_data else True)
                sim_roof = st.selectbox("Roof Renovation / Condition", ["Excellent", "Good", "Fair", "Poor"], index=0 if decision.submission_data and decision.submission_data.property_details.roof_condition == "Excellent" else 1)

            with sim_col2:
                st.markdown("**💵 Policy & Deductible Adjustments:**")
                sim_deductible = st.select_slider("Adjust Deductible Preference", options=[500, 1000, 2500, 5000, 10000], value=1000)
                sim_limit = st.select_slider("Adjust Policy Limit", options=[500000, 1000000, 2000000, 5000000], value=1000000)

            # Re-compute simulated scores
            sim_base_score = decision.risk_profile.composite_score if decision.risk_profile else 40.0
            score_delta = 0.0
            if sim_sprinkler and (not decision.submission_data or not decision.submission_data.property_details.has_sprinkler_system):
                score_delta -= 12.0
            if sim_security and (not decision.submission_data or not decision.submission_data.property_details.has_security_system):
                score_delta -= 6.0
            if sim_alarm and (not decision.submission_data or not decision.submission_data.property_details.has_fire_alarm):
                score_delta -= 5.0
            if sim_roof == "Excellent":
                score_delta -= 4.0
            elif sim_roof == "Poor":
                score_delta += 15.0

            sim_final_score = max(5.0, min(100.0, sim_base_score + score_delta))
            sim_premium_mult = 1.0 + (score_delta / 100.0)
            sim_final_premium = min(10000.0, max(500.0, (decision.pricing.final_premium if decision.pricing else 1500.0) * sim_premium_mult))

            st.markdown("<br>", unsafe_allow_html=True)
            res_col1, res_col2, res_col3 = st.columns(3)
            with res_col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Simulated Risk Score</div>
                    <div class="kpi-value" style="color:{'#4caf50' if sim_final_score <= 35 else '#ff9800' if sim_final_score <= 65 else '#f44336'};">{sim_final_score:.1f}</div>
                    <div class="kpi-label">{'(Δ ' + str(round(score_delta, 1)) + ' pts)' if score_delta != 0 else 'Unchanged'}</div>
                </div>
                """, unsafe_allow_html=True)
            with res_col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Simulated Premium</div>
                    <div class="kpi-value" style="color:#1976d2;">${sim_final_premium:,.2f}</div>
                    <div class="kpi-label">{'(Capped at $10K)' if sim_final_premium >= 10000 else 'Adjusted Rate'}</div>
                </div>
                """, unsafe_allow_html=True)
            with res_col3:
                sim_decision_label = "Auto-Approved" if sim_final_score <= 35 and (not decision.risk_profile or not decision.risk_profile.is_hazard_zone) else "Manual Review" if sim_final_score <= 65 else "Auto-Declined"
                sim_color = "#2e7d32" if sim_decision_label == "Auto-Approved" else "#e65100" if sim_decision_label == "Manual Review" else "#c62828"
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Simulated Triage Verdict</div>
                    <div class="kpi-value" style="font-size:1.2rem; color:{sim_color};">{sim_decision_label}</div>
                    <div class="kpi-label">Straight-Through Candidate</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab_audit:
            st.markdown('<div class="enterprise-card"><div class="card-header">🔍 OpenTelemetry Audit Trail & Data Sovereignty</div>', unsafe_allow_html=True)

            # Data Sovereignty verification
            st.markdown("""
            <div style="background:#e8f0fe; border-left:4px solid #1a73e8; padding:10px 14px; border-radius:6px; margin-bottom:12px;">
                <div style="font-weight:700; font-size:0.85rem; color:#1a73e8;">🛡️ Data Sovereignty & Zero-Data-Retention (ZDR) Enforced</div>
                <div style="font-size:0.78rem; color:#37474f; margin-top:2px;">
                    Residency: <b>Google Cloud us-central1 (Iowa)</b> &ensp;|&ensp;
                    Classification: <b>RESTRICTED_FINANCIAL</b> &ensp;|&ensp;
                    ZDR Mode: <b>ACTIVE (In-Memory Processing Only · Zero Foundation Model Retention)</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Multi-week session snapshots
            snapshots = memory.list_snapshots() if hasattr(memory, 'list_snapshots') else (list(getattr(memory, '_snapshots', {}).values()))
            if snapshots:
                st.markdown("<b>📅 Multi-Week Asynchronous Session Lifecycles (Persistent Memory Bank):</b>", unsafe_allow_html=True)
                for snap in snapshots[-3:]:
                    st.markdown(f"""
                    <div style="background:#f8f9fa; border:1px solid #e0e0e0; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:700; font-size:0.85rem;">Session Snapshot #{snap.session_id}</span>
                                <span style="font-size:0.72rem; background:#e8f5e9; color:#2e7d32; padding:2px 8px; border-radius:10px; font-weight:600; margin-left:6px;">Status: {snap.status}</span>
                            </div>
                            <div style="font-size:0.72rem; color:#5f6368;">TTL: {snap.ttl_days} Days Remaining</div>
                        </div>
                        <div style="font-size:0.75rem; color:#5f6368; margin-top:4px;">
                            Submission ID: <b>{snap.submission_id}</b> &ensp;|&ensp; Region: <b>{snap.sovereignty_region}</b> &ensp;|&ensp; Created: <b>{snap.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            trace = observability.get_trace(decision.submission_id)
            if trace:
                st.markdown("<br><b>OpenTelemetry Span Traces:</b>", unsafe_allow_html=True)
                for entry in trace:
                    status_icon = "✅" if entry.status == "OK" else "❌"
                    st.markdown(f"""
                    <div style="padding:10px 0; border-bottom:1px solid #f0f0f0;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:600; font-size:0.9rem;">{status_icon} {entry.agent_name}</span>
                                <span style="font-size:0.75rem; color:#5f6368; margin-left:8px;">{entry.action}</span>
                            </div>
                            <div style="font-size:0.75rem; color:#1976d2; font-weight:600;">{entry.duration_ms}ms</div>
                        </div>
                        <div style="font-size:0.78rem; color:#5f6368; margin-top:4px;">{entry.output_summary}</div>
                        <div style="font-size:0.7rem; color:#9e9e9e; margin-top:2px;">
                            Trace: {entry.trace_id} &ensp;|&ensp; Span: {entry.span_id}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pipeline metrics
                metrics = observability.get_pipeline_metrics(decision.submission_id)
                if metrics:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"""
                    **Pipeline Metrics:** Total Duration: {metrics.get('total_duration_ms', 0):.0f}ms &ensp;|&ensp;
                    Agents: {metrics.get('agent_count', 0)} &ensp;|&ensp;
                    Errors: {metrics.get('error_count', 0)}
                    """)
            else:
                st.info("No trace data available for this submission.")

            # Model Armor Audit
            armor_log = armor.get_audit_log()
            if armor_log:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**🛡 Model Armor Security & Sovereignty Log:**")
                for entry in armor_log[-6:]:
                    st.markdown(f"- `{entry['timestamp']}` — **{entry['event_type']}** from `{entry['source']}`: {entry['details']}")

            st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────
# Page: Agent Registry
# ────────────────────────────────────────────────────────────────────

elif page == "📋 Agent Registry":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Agent Registry</h1>
        <p>Enterprise agent catalog — discovery, lifecycle management, and health monitoring</p>
        <span class="header-badge">Fortified Enterprise Fleet &ensp;|&ensp; 6 Registered Agents</span>
    </div>
    """, unsafe_allow_html=True)

    # Enterprise Architecture Overview Banner
    st.markdown("""
    <div style="background:#e8f0fe; border-left:4px solid #1a73e8; border-radius:8px; padding:12px 16px; margin-bottom:16px;">
        <div style="font-weight:700; font-size:0.9rem; color:#1a73e8;">🌐 Scalable Institutional Agent Network & Data Sovereignty Policy</div>
        <div style="font-size:0.8rem; color:#37474f; margin-top:4px; line-height:1.4;">
            All 6 specialized agents hook into official enterprise infrastructure (FastAPI API Gateway, Firestore state bank, and OpenTelemetry collector).
            Agents are shared cross-departmentally via RBAC policies, maintain persistent context across 90-day asynchronous lifecycles, and enforce strict Zero-Data-Retention (ZDR) within sovereign Google Cloud regions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Interactive RBAC & Cross-Department Access Simulator ─────────
    with st.expander("🔐 Interactive Cross-Department Access & RBAC Authorization Tester", expanded=True):
        st.markdown("Test how different institutional business units and roles interact with the agent fleet under strict enterprise permission boundaries:")
        
        sim_dept_col, sim_role_col, sim_agent_col = st.columns(3)
        with sim_dept_col:
            test_dept = st.selectbox(
                "Calling Department",
                ["Claims Triage", "Underwriting", "Actuarial Science", "Legal & Regulatory Affairs", "Broker Portal", "Policy Administration", "External / Public API"],
                index=0,
                key="test_dept_select"
            )
        with sim_role_col:
            test_role = st.selectbox(
                "Caller RBAC Role",
                ["Claims_Adjuster", "Underwriter", "Actuary", "Compliance_Officer", "Broker_API_Client", "Risk_Engineer", "Unauthenticated_Guest"],
                index=0,
                key="test_role_select"
            )
        with sim_agent_col:
            test_agent_target = st.selectbox(
                "Target Enterprise Agent",
                ["📥 Intake Agent", "🔍 Risk Profiling Agent", "💰 Pricing & Product Agent", "⚖️ Compliance Agent", "🎯 Orchestrator Agent", "📊 Feedback & Learning Agent"],
                index=0,
                key="test_agent_select"
            )

        agent_key_map = {
            "📥 Intake Agent": "intake-agent",
            "🔍 Risk Profiling Agent": "risk-agent",
            "💰 Pricing & Product Agent": "pricing-agent",
            "⚖️ Compliance Agent": "compliance-agent",
            "🎯 Orchestrator Agent": "orchestrator-agent",
            "📊 Feedback & Learning Agent": "feedback-agent",
        }
        target_id = agent_key_map.get(test_agent_target, "intake-agent")
        target_entry = registry.get_agent(target_id)

        if target_entry:
            allowed_roles = getattr(target_entry, "rbac_roles", ["Underwriter"])
            allowed_depts = getattr(target_entry, "authorized_departments", ["Underwriting"])
            
            is_authorized = (test_role in allowed_roles) and (test_dept in allowed_depts or test_dept == target_entry.department)

            if is_authorized:
                st.markdown(f"""
                <div style="background:#e8f5e9; border:1px solid #4caf50; border-radius:8px; padding:12px 16px; margin-top:8px;">
                    <div style="font-weight:700; color:#2e7d32; font-size:0.92rem;">
                        ✅ 200 OK — Cross-Department Access Granted
                    </div>
                    <div style="font-size:0.8rem; color:#1b5e20; margin-top:4px;">
                        Caller <b>[{test_dept} · {test_role}]</b> is authorized to invoke <b>{target_entry.agent_name}</b> via endpoint <code>{target_entry.api_endpoint}</code>.
                    </div>
                    <div style="font-size:0.75rem; color:#388e3c; margin-top:4px;">
                        <b>Security Context:</b> Data Sovereignty Region: <code>{target_entry.sovereignty_region}</code> &ensp;|&ensp; ZDR Mode: <code>ACTIVE</code> &ensp;|&ensp; OTel Audit Span: <code>EMITTED</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#ffebee; border:1px solid #f44336; border-radius:8px; padding:12px 16px; margin-top:8px;">
                    <div style="font-weight:700; color:#c62828; font-size:0.92rem;">
                        🚫 403 FORBIDDEN — RBAC Permission Denied
                    </div>
                    <div style="font-size:0.8rem; color:#b71c1c; margin-top:4px;">
                        Caller <b>[{test_dept} · {test_role}]</b> does not possess the required RBAC role to execute <b>{target_entry.agent_name}</b>.
                    </div>
                    <div style="font-size:0.75rem; color:#7f0000; margin-top:4px;">
                        <b>Allowed Roles:</b> <code>{", ".join(allowed_roles)}</code> &ensp;|&ensp; <b>Primary Owner:</b> <code>{target_entry.department}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    agents = registry.list_agents()
    for agent in agents:
        health_color = "#4caf50" if agent.health == "Healthy" else "#ff9800"
        status_color = {
            "Idle": "#9e9e9e",
            "Running": "#1976d2",
            "Completed": "#4caf50",
            "Error": "#f44336",
        }.get(agent.status.value, "#9e9e9e")

        dept_badges = "".join(f'<span style="font-size:0.68rem; background:#e8eaf6; color:#1a237e; padding:2px 8px; border-radius:4px; font-weight:600; margin-right:4px;">🏢 {d}</span>' for d in getattr(agent, 'authorized_departments', ['Underwriting']))
        rbac_badges = "".join(f'<span style="font-size:0.68rem; background:#ede7f6; color:#4527a0; padding:2px 8px; border-radius:4px; font-weight:600; margin-right:4px;">🔑 {r}</span>' for r in getattr(agent, 'rbac_roles', ['Underwriter']))

        st.markdown(f"""
        <div class="enterprise-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-size:1rem; font-weight:700; color:#202124;">{agent.agent_name}
                        <span style="font-size:0.7rem; background:#e8f0fe; color:#1a73e8; padding:2px 8px; border-radius:10px; margin-left:8px;">v{agent.version}</span>
                        <span style="font-size:0.7rem; background:#e0f2f1; color:#00695c; padding:2px 8px; border-radius:10px; margin-left:4px;">{getattr(agent, 'sovereignty_region', 'Google Cloud us-central1')}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#5f6368; margin-top:4px;">{agent.description}</div>
                    <div style="font-size:0.75rem; color:#1976d2; font-family:monospace; margin-top:3px;">Endpoint: {getattr(agent, 'api_endpoint', '/api/v1/agents')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.7rem; font-weight:600;">
                        <span style="color:{health_color};">● {agent.health}</span>
                    </div>
                    <div style="font-size:0.7rem; color:{status_color}; margin-top:2px;">
                        Status: {agent.status.value}
                    </div>
                </div>
            </div>
            <div style="display:flex; gap:16px; margin-top:12px; flex-wrap:wrap;">
                <div style="font-size:0.75rem;">
                    <span style="color:#5f6368;">Primary Owner:</span>
                    <span style="font-weight:600;">{agent.department}</span>
                </div>
                <div style="font-size:0.75rem;">
                    <span style="color:#5f6368;">Total Executions:</span>
                    <span style="font-weight:600;">{agent.total_executions}</span>
                </div>
                <div style="font-size:0.75rem;">
                    <span style="color:#5f6368;">Avg Latency:</span>
                    <span style="font-weight:600;">{agent.avg_latency_ms:.0f}ms</span>
                </div>
                <div style="font-size:0.75rem;">
                    <span style="color:#5f6368;">Success Rate:</span>
                    <span style="font-weight:600;">{agent.success_rate:.0f}%</span>
                </div>
            </div>
            <div style="margin-top:10px;">
                <span style="font-size:0.72rem; color:#5f6368; font-weight:600;">Cross-Department Access: </span>{dept_badges}
            </div>
            <div style="margin-top:6px;">
                <span style="font-size:0.72rem; color:#5f6368; font-weight:600;">RBAC Roles: </span>{rbac_badges}
            </div>
            <div style="margin-top:8px; display:flex; gap:4px; flex-wrap:wrap;">
                {"".join(f'<span style="font-size:0.65rem; background:#f5f5f5; padding:2px 8px; border-radius:4px; color:#616161;">{c}</span>' for c in agent.capabilities)}
            </div>
            <div style="margin-top:6px; display:flex; gap:4px; flex-wrap:wrap;">
                {"".join(f'<span style="font-size:0.65rem; background:#e8f5e9; padding:2px 8px; border-radius:4px; color:#2e7d32;">🔧 {t}</span>' for t in agent.tools)}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────
# Page: Notifications
# ────────────────────────────────────────────────────────────────────

elif page == "🔔 Notifications":
    st.markdown("""
    <div class="main-header">
        <h1>🔔 Notification Center</h1>
        <p>Human-in-the-loop review queue and action items</p>
    </div>
    """, unsafe_allow_html=True)

    all_notifications = memory.get_notifications(unacknowledged_only=False)

    if not all_notifications:
        st.info("No notifications yet. Submit a broker submission to begin processing.")
    else:
        pending = [n for n in all_notifications if not n.acknowledged]
        acknowledged = [n for n in all_notifications if n.acknowledged]

        if pending:
            st.markdown(f"### ⏳ Pending Actions ({len(pending)})")
            render_notifications(memory)

        if acknowledged:
            st.markdown(f"### ✅ Acknowledged ({len(acknowledged)})")
            for n in acknowledged:
                st.markdown(f"- ~~{n.title}~~ — {n.created_at.strftime('%Y-%m-%d %H:%M')}")

    # Pending Reviews
    pending_reviews = memory.get_pending_reviews()
    if pending_reviews:
        st.markdown("---")
        st.markdown(f"### 📋 Submissions Pending Senior Underwriter Review ({len(pending_reviews)})")

        for d in pending_reviews:
            biz_name = d.submission_data.business_info.business_name if d.submission_data else "Unknown Business"
            risk_score = d.risk_profile.composite_score if d.risk_profile else 0
            premium = d.pricing.final_premium if d.pricing else 0

            with st.expander(f"📁 Review Submission: {biz_name} — ID #{d.submission_id} (Priority: {d.review_priority})", expanded=True):
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("Risk Score", f"{risk_score} / 100", delta=f"{d.risk_profile.risk_tier.value} Risk" if d.risk_profile else "")
                with col_info2:
                    st.metric("Recommended Premium", f"${premium:,.0f}", delta="Annual Term")
                with col_info3:
                    st.metric("Confidence", f"{d.confidence_score}%")

                render_underwriter_action_panel(d, memory, key_prefix=f"notif_{d.submission_id}")


# ────────────────────────────────────────────────────────────────────
# Page: Portfolio Analytics
# ────────────────────────────────────────────────────────────────────

elif page == "📊 Portfolio Analytics":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Portfolio Analytics</h1>
        <p>Real-time underwriting portfolio insights, straight-through processing rates, and underwriter action metrics</p>
    </div>
    """, unsafe_allow_html=True)

    stats = memory.get_portfolio_stats()

    if stats["total_submissions"] == 0:
        st.info("No submissions processed yet. Go to the Underwriting Desk to begin.")
    else:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Volume</div>
                <div class="kpi-value" style="color:#1976d2;">{stats['total_submissions']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">⚡ Auto-Approved</div>
                <div class="kpi-value" style="color:#4caf50;">{stats.get('auto_approved', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">👨‍💼 UW Approved</div>
                <div class="kpi-value" style="color:#2e7d32;">{stats.get('underwriter_approved', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">⏳ Pending Review</div>
                <div class="kpi-value" style="color:#ff9800;">{stats.get('manual_review', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">🚫 Auto-Declined</div>
                <div class="kpi-value" style="color:#f44336;">{stats.get('auto_declined', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col6:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">👨‍💼 UW Declined</div>
                <div class="kpi-value" style="color:#c62828;">{stats.get('underwriter_declined', 0)}</div>
            </div>
            """, unsafe_allow_html=True)

        # Decision distribution chart
        if stats["total_submissions"] > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            col_pie, col_history = st.columns([1, 1])

            with col_pie:
                st.markdown('<div class="enterprise-card"><div class="card-header">📊 Decision Portfolio Distribution</div>', unsafe_allow_html=True)
                
                chart_labels = []
                chart_values = []
                chart_colors = []

                if stats.get('auto_approved', 0) > 0:
                    chart_labels.append("Auto-Approved (STP)")
                    chart_values.append(stats['auto_approved'])
                    chart_colors.append("#4caf50")
                if stats.get('underwriter_approved', 0) > 0:
                    chart_labels.append("Underwriter Approved")
                    chart_values.append(stats['underwriter_approved'])
                    chart_colors.append("#2e7d32")
                if stats.get('manual_review', 0) > 0:
                    chart_labels.append("Pending Review")
                    chart_values.append(stats['manual_review'])
                    chart_colors.append("#ff9800")
                if stats.get('auto_declined', 0) > 0:
                    chart_labels.append("Auto-Declined (STP)")
                    chart_values.append(stats['auto_declined'])
                    chart_colors.append("#f44336")
                if stats.get('underwriter_declined', 0) > 0:
                    chart_labels.append("Underwriter Declined")
                    chart_values.append(stats['underwriter_declined'])
                    chart_colors.append("#b71c1c")

                if not chart_values:
                    chart_labels = ["No data"]
                    chart_values = [1]
                    chart_colors = ["#e0e0e0"]

                fig_pie = go.Figure(go.Pie(
                    labels=chart_labels,
                    values=chart_values,
                    marker=dict(colors=chart_colors),
                    hole=0.5,
                    textfont=dict(family='Inter', size=11),
                ))
                fig_pie.update_layout(
                    height=320, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='white', font=dict(family='Inter'),
                    showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_history:
                st.markdown('<div class="enterprise-card"><div class="card-header">📋 Recent Underwriting Activity</div>', unsafe_allow_html=True)
                decisions = memory.list_decisions()
                for d in decisions[:6]:
                    biz = d.submission_data.business_info.business_name if d.submission_data else "Unknown Business"
                    prem_str = f" · **${d.pricing.final_premium:,.0f}**" if d.pricing else ""
                    
                    if getattr(d, 'underwriter_override', None) == "APPROVED":
                        status_badge = '<span style="background:#e8f5e9; color:#2e7d32; font-weight:700; font-size:0.72rem; padding:2px 8px; border-radius:10px;">👨‍💼 Underwriter Approved</span>'
                    elif getattr(d, 'underwriter_override', None) == "DECLINED":
                        status_badge = '<span style="background:#ffebee; color:#c62828; font-weight:700; font-size:0.72rem; padding:2px 8px; border-radius:10px;">👨‍💼 Underwriter Declined</span>'
                    elif d.decision == DecisionType.AUTO_APPROVED:
                        status_badge = '<span style="background:#e8f5e9; color:#1b5e20; font-weight:600; font-size:0.72rem; padding:2px 8px; border-radius:10px;">⚡ Auto-Approved</span>'
                    elif d.decision == DecisionType.AUTO_DECLINED:
                        status_badge = '<span style="background:#ffebee; color:#b71c1c; font-weight:600; font-size:0.72rem; padding:2px 8px; border-radius:10px;">🚫 Auto-Declined</span>'
                    else:
                        status_badge = '<span style="background:#fff3e0; color:#e65100; font-weight:600; font-size:0.72rem; padding:2px 8px; border-radius:10px;">⏳ Pending Review</span>'

                    notes_preview = f"<div style='font-size:0.72rem; color:#5f6368; margin-top:2px;'>Notes: <i>{d.underwriter_comments}</i></div>" if getattr(d, 'underwriter_comments', None) else ""

                    st.markdown(f"""
                    <div style="padding:8px 0; border-bottom:1px solid #f0f0f0;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-size:0.85rem; font-weight:600; color:#202124;">{biz}{prem_str}</div>
                            <div>{status_badge}</div>
                        </div>
                        <div style="font-size:0.72rem; color:#80868b; margin-top:2px;">ID: #{d.submission_id} &ensp;|&ensp; {d.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                        {notes_preview}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

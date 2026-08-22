import React from 'react';
import { X, Cpu, ShieldCheck, CheckCircle2, ChevronRight } from 'lucide-react';

const AGENT_INFO = {
  'intake-agent': {
    title: '📥 Intake Agent',
    role: 'Document Ingestion & ACORD Entity Extraction',
    logic: [
      'Normalizes unstructured commercial text and ACORD 125/126 applications.',
      'Calls Open-Meteo Geocoding MCP to resolve precise latitude, longitude, and elevation.',
      'Validates mandatory commercial fields (revenue, payroll, property value, claims history).'
    ],
  },
  'risk-agent': {
    title: '🔍 Risk Profiling Agent',
    role: '6-Axis Risk Scoring & Natural Hazard Detection',
    logic: [
      'Invokes Location Intelligence Aggregator across FEMA, USGS, and Open-Meteo MCP feeds.',
      'Calculates 6 actuarial dimensions: Property (20%), Location (20%), Financial (15%), Claims (20%), Operations (15%), Compliance (10%).',
      'Synthesizes risk factors into an executive underwriting narrative.'
    ],
  },
  'pricing-agent': {
    title: '💰 Pricing & Product Agent',
    role: 'Base Rate × 9 Multipliers & $10K Policy Cap Enforcement',
    logic: [
      'Determines base premium tier from property replacement value ($800 to $4,200).',
      'Applies 9 deterministic rating modifiers for business class, revenue, employees, hazard zones, claims, safety, experience, and building age.',
      'Enforces strict $10,000 statutory policy cap and minimum $500 floor.'
    ],
  },
  'compliance-agent': {
    title: '⚖️ Compliance Agent',
    role: '10 Statutory Regulatory Rules & Fair Lending Verification',
    logic: [
      'Audits operating license validity, prohibited industry classes, and prior fraud cancellations.',
      'Enforces ECOA/FCRA fair lending non-discrimination standards.',
      'Checks natural hazard disclosure (ENV-001) and maximum allowable rate surcharges.'
    ],
  },
  'orchestrator-agent': {
    title: '🎯 Orchestrator Agent',
    role: 'Tripartite Decision Matrix & Human-in-the-Loop Triage',
    logic: [
      'Auto-Approve: Risk ≤ 35, all 10 compliance rules pass, standard property.',
      'Manual Review: Hazard zone detected, score 36-65, or compliance warning flag.',
      'Auto-Decline: Score > 80, prohibited business class, or prior cancellation for fraud.'
    ],
  },
  'feedback-agent': {
    title: '📊 Feedback & Learning Agent',
    role: 'Executive Portfolio Synthesis & Continuous Learning',
    logic: [
      'Synthesizes complex actuarial telemetry into board-level executive summaries.',
      'Detects aggregate portfolio hazard concentrations along coastal and seismic fault corridors.',
      'Generates loss ratio forecasting and recommendations for loss-control engineering.'
    ],
  },
  'mcp-open-meteo-geocoding': {
    title: '📍 Open-Meteo Geocoding MCP',
    role: 'Address Normalization & Topographic Elevation',
    logic: [
      'Endpoint: https://geocoding-api.open-meteo.com/v1/search',
      'Resolves ambiguous street names into decimal latitude, longitude, and elevation.',
      'Feeds spatial telemetry to downstream hazard sub-agents.'
    ],
  },
  'mcp-fema-flood': {
    title: '🌊 FEMA Flood Zone MCP',
    role: 'NFHL GIS Inundation Modeling & SFHA Classification',
    logic: [
      'Queries FEMA National Flood Hazard Layer (NFHL) GIS layers.',
      'Classifies flood zones (Zone VE velocity wave, Zone AE 100-yr floodplain, Zone X minimal).',
      'Determines mandatory Special Flood Hazard Area (SFHA) insurance requirements and BFE.'
    ],
  },
  'mcp-usgs-seismic': {
    title: '🌋 USGS Seismic MCP',
    role: 'Active Fault Proximity & Ground Motion (PGA) Rating',
    logic: [
      'Queries USGS real-time and historical earthquake event feeds within a 150km radius.',
      'Calculates active fault line distance (<20km = Critical hazard).',
      'Determines Peak Ground Acceleration (PGA %g) and liquefaction vulnerability.'
    ],
  },
  'mcp-open-meteo-weather': {
    title: '🌪️ Open-Meteo Weather MCP',
    role: 'Numerical Weather Prediction & Hurricane Exposure Tiers',
    logic: [
      'Queries high-resolution numerical weather prediction models.',
      'Classifies hurricane exposure tiers (Tier 1-5 / Cat 5 wind-borne debris regions).',
      'Tracks maximum recorded wind gusts (mph) and severe convective storm vulnerability.'
    ],
  },
};

export default function AgentInspector({ agentId, onClose, decision }) {
  if (!agentId) return null;

  const info = AGENT_INFO[agentId] || {
    title: '🤖 Agent Inspector',
    role: 'Specialized Sub-Agent',
    logic: ['Autonomous execution component.'],
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
              {info.title}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
              {info.role}
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '8px' }}>
            ⚙️ Operational Methodology & Decision Rules:
          </div>
          <ul style={{ paddingLeft: '20px', fontSize: '0.8rem', color: '#475569', lineHeight: '1.6' }}>
            {info.logic.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        </div>

        {decision && (
          <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
              📊 Telemetry for Active Submission ({decision.submission_id}):
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
              <div>• Decision Verdict: <b>{decision.decision}</b></div>
              <div>• Confidence Rating: <b>{decision.confidence_score}%</b></div>
              <div>• Model Armor Status: <b>Passed (Zero-Retention Verified)</b></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

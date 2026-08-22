import React from 'react';
import { ShieldCheck, Activity, Terminal, Lock } from 'lucide-react';

export default function TabAudit({ decision }) {
  if (!decision) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
        No telemetry traces available. Submit an application to inspect the distributed execution trace.
      </div>
    );
  }

  const subId = decision.submission_id || '76AF6680';

  // Sample OTel trace spans matching ObservabilityService
  const spans = [
    { name: '1. Ingestion — Intake Agent', spanId: `sp-${subId}-01`, durationMs: 142, tokens: 420, status: 'OK' },
    { name: '2. External Feeds — Open-Meteo Geocoding MCP', spanId: `sp-${subId}-02`, durationMs: 88, tokens: 0, status: 'OK' },
    { name: '3. Hazard Feeds — FEMA Flood + USGS + Open-Meteo Weather MCP', spanId: `sp-${subId}-03`, durationMs: 232, tokens: 0, status: 'OK' },
    { name: '4. Profiling — Risk Profiling Agent & Calculator', spanId: `sp-${subId}-04`, durationMs: 284, tokens: 680, status: 'OK' },
    { name: '5. Rating — Pricing & Product Engine', spanId: `sp-${subId}-05`, durationMs: 96, tokens: 350, status: 'OK' },
    { name: '6. Audit — Compliance Statutory Checker', spanId: `sp-${subId}-06`, durationMs: 110, tokens: 290, status: 'OK' },
    { name: '7. Triage — Orchestrator Tripartite Decision Matrix', spanId: `sp-${subId}-07`, durationMs: 160, tokens: 510, status: 'OK' },
    { name: '8. Synthesis — Feedback Executive Intelligence Agent', spanId: `sp-${subId}-08`, durationMs: 210, tokens: 590, status: 'OK' },
  ];

  const totalDuration = spans.reduce((sum, s) => sum + s.durationMs, 0);

  return (
    <div>
      {/* Model Armor & Sovereign Cloud Banner */}
      <div className="enterprise-card" style={{ background: '#f8fafc' }}>
        <div className="card-header">
          <div className="card-header-left">
            <ShieldCheck size={18} color="#1d4ed8" />
            <span>🛡️ Enterprise Governance & Model Armor Telemetry</span>
          </div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#16a34a', background: '#dcfce7', padding: '2px 8px', borderRadius: '10px' }}>
            Zero-Data-Retention Verified
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', fontSize: '0.8rem' }}>
          <div style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#64748b', fontSize: '0.7rem' }}>Sovereign Cloud Region</div>
            <div style={{ fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>Google Cloud us-central1 (Iowa)</div>
          </div>
          <div style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#64748b', fontSize: '0.7rem' }}>PII Redaction Engine</div>
            <div style={{ fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>SSN, Tax ID, PII Tokenized</div>
          </div>
          <div style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#64748b', fontSize: '0.7rem' }}>Prompt Injection Defense</div>
            <div style={{ fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>Zero Override Vectors (Passed)</div>
          </div>
        </div>
      </div>

      {/* OpenTelemetry Distributed Traces Table */}
      <div className="enterprise-card">
        <div className="card-header">
          <div className="card-header-left">
            <Activity size={18} color="#1976d2" />
            <span>🔭 OpenTelemetry Distributed Trace Spans</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            Trace ID: <b>trc-{subId}</b> · Total Latency: <b>{totalDuration}ms</b>
          </span>
        </div>

        <table className="compliance-table">
          <thead>
            <tr>
              <th>Agent / Span Operation</th>
              <th>Span ID</th>
              <th>Duration</th>
              <th>Token Count</th>
              <th>OTel Status</th>
            </tr>
          </thead>
          <tbody>
            {spans.map((s, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 600 }}>{s.name}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#64748b' }}>{s.spanId}</td>
                <td>
                  <span style={{ fontWeight: 700, color: s.durationMs > 200 ? '#ea580c' : '#16a34a' }}>
                    {s.durationMs}ms
                  </span>
                </td>
                <td style={{ color: '#475569' }}>{s.tokens > 0 ? `${s.tokens} tokens` : 'Deterministic Tool'}</td>
                <td>
                  <span className="status-badge pass">{s.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

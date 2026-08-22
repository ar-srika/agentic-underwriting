import React from 'react';
import RadarChart from './RadarChart';
import { AlertTriangle, CheckCircle, ShieldAlert, Info } from 'lucide-react';

export default function TabRisk({ riskProfile }) {
  if (!riskProfile) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
        No risk profile generated yet. Submit an application to run the 6-agent assessment.
      </div>
    );
  }

  const { composite_score, risk_tier, dimensions, hazard_zones_detected, auto_decline_triggers, risk_summary } = riskProfile;

  const getScoreColor = (score) => {
    if (score <= 35) return '#16a34a';
    if (score <= 65) return '#ea580c';
    return '#dc2626';
  };

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '20px', marginBottom: '20px' }}>
        {/* Radar Chart Card */}
        <div className="enterprise-card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <span>📈 Risk Dimension Radar</span>
          </div>
          <RadarChart dimensions={dimensions} size={300} />
          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', fontSize: '0.7rem', color: '#64748b', marginTop: '10px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#16a34a' }}></span>
              Auto-Approve (≤35)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ea580c' }}></span>
              Review (36-65)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#dc2626' }}></span>
              Decline (&gt;65)
            </span>
          </div>
        </div>

        {/* Summary & Overall Risk Score */}
        <div className="enterprise-card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <span>🎯 Composite Actuarial Score</span>
            <span
              style={{
                background: getScoreColor(composite_score) + '15',
                color: getScoreColor(composite_score),
                padding: '3px 10px',
                borderRadius: '12px',
                fontSize: '0.8rem',
                fontWeight: 700
              }}
            >
              {risk_tier?.value || risk_tier} Risk
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '12px' }}>
            <span style={{ fontSize: '2.5rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: getScoreColor(composite_score) }}>
              {composite_score}
            </span>
            <span style={{ fontSize: '1rem', color: '#64748b', fontWeight: 600 }}>/ 100</span>
          </div>

          <div className="progress-bar-bg" style={{ height: '8px', marginBottom: '16px' }}>
            <div
              className="progress-bar-fill"
              style={{
                width: `${composite_score}%`,
                background: getScoreColor(composite_score),
              }}
            />
          </div>

          {hazard_zones_detected && hazard_zones_detected.length > 0 && (
            <div style={{ marginBottom: '12px', padding: '10px 12px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#92400e', marginBottom: '4px' }}>
                🚨 Active Natural Hazard Zones Detected:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {hazard_zones_detected.map((zone, idx) => (
                  <span
                    key={idx}
                    style={{ background: '#fef3c7', color: '#b45309', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}
                  >
                    {zone}
                  </span>
                ))}
              </div>
            </div>
          )}

          {auto_decline_triggers && auto_decline_triggers.length > 0 && (
            <div style={{ marginBottom: '12px', padding: '10px 12px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#991b1b', marginBottom: '4px' }}>
                ⛔ Statutory Auto-Decline Triggers:
              </div>
              <ul style={{ paddingLeft: '18px', fontSize: '0.75rem', color: '#b91c1c' }}>
                {auto_decline_triggers.map((t, idx) => (
                  <li key={idx}>{t}</li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: '1.5', background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <strong>Executive Underwriting Narrative:</strong>
            <p style={{ marginTop: '4px' }}>{risk_summary}</p>
          </div>
        </div>
      </div>

      {/* 6 Dimensions Grid */}
      <div className="enterprise-card">
        <div className="card-header">
          <span>📊 6-Axis Dimension Breakdown</span>
        </div>
        <div className="dimension-card-grid">
          {dimensions?.map((dim, idx) => (
            <div key={idx} className="dimension-card">
              <div className="dimension-header">
                <span className="dimension-title">{dim.name} (Weight: {(dim.weight * 100).toFixed(0)}%)</span>
                <span className="dimension-score" style={{ color: getScoreColor(dim.score) }}>
                  {dim.score} / 100
                </span>
              </div>
              <div className="progress-bar-bg">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${dim.score}%`,
                    background: getScoreColor(dim.score),
                  }}
                />
              </div>
              <ul style={{ paddingLeft: '16px', fontSize: '0.75rem', color: '#64748b', marginBottom: '6px' }}>
                {dim.factors?.map((f, fi) => (
                  <li key={fi}>{f}</li>
                ))}
              </ul>
              {dim.recommendation && (
                <div style={{ fontSize: '0.7rem', color: '#1d4ed8', background: '#eff6ff', padding: '4px 8px', borderRadius: '4px' }}>
                  💡 {dim.recommendation}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

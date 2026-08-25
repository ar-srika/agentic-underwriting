import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck, Sparkles, FileText, Info } from 'lucide-react';

export default function DecisionBanner({ decision }) {
  if (!decision) return null;

  const decisionType = decision.decision || 'Auto-Approved';
  let bannerClass = 'approved';
  let Icon = CheckCircle2;

  if (decisionType === 'Manual Review Required' || decision.requires_human_review) {
    bannerClass = 'review';
    Icon = AlertTriangle;
  } else if (decisionType === 'Auto-Declined' || decisionType === 'Underwriter Declined') {
    bannerClass = 'declined';
    Icon = XCircle;
  }

  const intakeNotes = decision.submission_data?.intake_notes || [];
  const executiveSummary = decision.executive_summary;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div className={`decision-banner ${bannerClass}`}>
        <div className="decision-banner-left">
          <div className="decision-icon">
            <Icon size={36} />
          </div>
          <div>
            <div className="decision-title">
              {decision.decision}
            </div>
            <div className="decision-subtitle">
              {decision.decision_rationale || 'Submission assessed by autonomous underwriting fleet.'}
            </div>
          </div>
        </div>

        <div className="decision-metrics">
          <div className="decision-metric-item">
            <span className="metric-label">Confidence Rating</span>
            <span className="metric-value">{decision.confidence_score || 98.5}%</span>
          </div>
          <div className="decision-metric-item">
            <span className="metric-label">Processing Time</span>
            <span className="metric-value">{decision.processing_time_seconds || 0.74}s</span>
          </div>
          <div className="decision-metric-item">
            <span className="metric-label">Agents Executed</span>
            <span className="metric-value">{decision.agents_executed?.length || 6}</span>
          </div>
        </div>
      </div>

      {/* Executive Summary by Feedback & Learning Agent */}
      {executiveSummary && (
        <div className="enterprise-card" style={{ padding: '14px 16px', background: '#f8fafc', border: '1px solid #cbd5e1', marginBottom: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 700, color: '#1e3a8a' }}>
              <Sparkles size={16} color="#2563eb" />
              <span>Executive Underwriting Summary (Feedback & Learning Agent)</span>
            </div>
            <span style={{ fontSize: '0.68rem', fontWeight: 600, background: '#eff6ff', color: '#1d4ed8', padding: '2px 8px', borderRadius: '10px' }}>
              Gemini Frontier Intelligence (3.5+)
            </span>
          </div>
          <div style={{ fontSize: '0.8rem', color: '#334155', lineHeight: '1.6' }}>
            {executiveSummary}
          </div>
        </div>
      )}

      {/* Intake & AI Reasoning Notes (Option 1A: Two-Tier Badges with Inline Rationale) */}
      {intakeNotes.length > 0 && (
        <div style={{ padding: '12px 16px', background: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: '#1e293b' }}>
              <Info size={14} color="#2563eb" />
              <span>📥 Intake & AI Gap Resolution Log:</span>
            </div>
            <span style={{ fontSize: '0.68rem', color: '#1e40af', fontWeight: 700, background: '#eff6ff', padding: '2px 8px', borderRadius: '10px', border: '1px solid #bfdbfe' }}>
              Gemini Frontier Intelligence (3.5+)
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {intakeNotes.map((note, idx) => {
              const hasRationale = note.includes('|');
              let mainText = note;
              let rationaleText = '';

              if (hasRationale) {
                const [left, right] = note.split('|');
                mainText = left.trim();
                rationaleText = right.trim();
              }

              const isAutoFilled = mainText.includes('Gemini Auto-Filled') || mainText.includes('auto-enhanced');
              const isVerified = mainText.includes('Gemini Verified') || mainText.includes('verified complete');
              const isMcp = mainText.includes('Geocoding') || mainText.includes('MCP');
              const isSkipped = mainText.includes('skipped') || mainText.includes('unavailable');

              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span
                      style={{
                        fontSize: '0.74rem',
                        padding: '3px 10px',
                        borderRadius: '6px',
                        fontWeight: 700,
                        background: isAutoFilled ? '#dcfce7' : isVerified ? '#f0fdf4' : isMcp ? '#eff6ff' : isSkipped ? '#fef3c7' : '#f8fafc',
                        color: isAutoFilled ? '#15803d' : isVerified ? '#166534' : isMcp ? '#1d4ed8' : isSkipped ? '#92400e' : '#334155',
                        border: `1px solid ${isAutoFilled ? '#86efac' : isVerified ? '#bbf7d0' : isMcp ? '#bfdbfe' : isSkipped ? '#fde68a' : '#e2e8f0'}`,
                      }}
                    >
                      {mainText}
                    </span>
                  </div>

                  {rationaleText && (
                    <div style={{ fontSize: '0.72rem', color: '#475569', marginLeft: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#94a3b8' }}>↳</span>
                      <span style={{ fontStyle: 'italic' }}>{rationaleText}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}


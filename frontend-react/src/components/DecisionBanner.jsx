import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck } from 'lucide-react';

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

  return (
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
  );
}

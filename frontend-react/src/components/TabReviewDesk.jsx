import React, { useState } from 'react';
import { UserCheck, CheckCircle2, XCircle, FileSignature, AlertTriangle } from 'lucide-react';

export default function TabReviewDesk({ decision, onOverrideDecision }) {
  const [comments, setComments] = useState('');
  const [overrideStatus, setOverrideStatus] = useState(null);

  if (!decision) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
        No active submission in the underwriter queue.
      </div>
    );
  }

  const handleAction = async (action) => {
    setOverrideStatus(action);
    if (onOverrideDecision) {
      await onOverrideDecision({
        submissionId: decision.submission_id,
        decisionType: action,
        comments,
      });
    }
  };

  const isReviewed = decision.decision === 'Underwriter Approved' || decision.decision === 'Underwriter Declined' || overrideStatus;

  return (
    <div className="enterprise-card">
      <div className="card-header">
        <div className="card-header-left">
          <FileSignature size={18} color="#1976d2" />
          <span>👨‍💼 Senior Underwriter Binding & Override Desk</span>
        </div>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>
          Authority Level: Tier 3 Commercial Binding ($1,000,000 Limit)
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        {/* Triage Summary */}
        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '8px' }}>
            📋 Application Triage State
          </div>
          <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: '1.6' }}>
            <div>• Submission ID: <b>{decision.submission_id}</b></div>
            <div>• Current Decision: <b>{decision.decision}</b></div>
            <div>• Risk Composite Score: <b>{decision.risk_profile?.composite_score}/100</b></div>
            <div>• Calculated Premium: <b>${decision.pricing?.final_premium?.toLocaleString()}</b></div>
            <div>• Review Priority: <span style={{ color: '#ea580c', fontWeight: 700 }}>{decision.review_priority || 'Standard'}</span></div>
          </div>
        </div>

        {/* Hazard & Review Reasons */}
        <div style={{ background: '#fffbeb', padding: '16px', borderRadius: '8px', border: '1px solid #fde68a' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#92400e', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={16} />
            <span>Reason Requiring Human Review</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#b45309', lineHeight: '1.5' }}>
            {decision.reviewer_notifications && decision.reviewer_notifications.length > 0 ? (
              decision.reviewer_notifications.map((notif, i) => <div key={i}>• {notif}</div>)
            ) : (
              <div>• Natural hazard zone detected or composite score within human verification corridor (36-65).</div>
            )}
          </div>
        </div>
      </div>

      {/* Underwriter Comments Box */}
      <div className="form-group">
        <label className="form-label">
          ✍️ Senior Underwriter Endorsement Notes & Rationale:
        </label>
        <textarea
          className="form-textarea"
          style={{ minHeight: '100px' }}
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Enter conditional endorsement terms, loss-control warranties, or underwriter rationale..."
          disabled={isReviewed}
        />
      </div>

      {/* Action Buttons */}
      {!isReviewed ? (
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            type="button"
            className="submit-btn"
            style={{ background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)', flex: 1 }}
            onClick={() => handleAction('APPROVED')}
          >
            <CheckCircle2 size={18} />
            <span>✅ Approve & Bind Policy (Underwriter Override)</span>
          </button>
          <button
            type="button"
            className="submit-btn"
            style={{ background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)', flex: 1 }}
            onClick={() => handleAction('DECLINED')}
          >
            <XCircle size={18} />
            <span>🚫 Decline Submission (Underwriter Record)</span>
          </button>
        </div>
      ) : (
        <div style={{ padding: '14px', background: overrideStatus === 'APPROVED' || decision.decision === 'Underwriter Approved' ? '#f0fdf4' : '#fef2f2', borderRadius: '8px', border: '1px solid #bbf7d0', textAlign: 'center' }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: overrideStatus === 'APPROVED' || decision.decision === 'Underwriter Approved' ? '#15803d' : '#b91c1c' }}>
            {overrideStatus === 'APPROVED' || decision.decision === 'Underwriter Approved'
              ? '🎉 Policy Approved & Bound by Senior Underwriter (Override Complete)'
              : '🚫 Policy Formally Declined by Senior Underwriter'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Recorded in 90-day cold-storage Memory Bank snapshot.
          </div>
        </div>
      )}
    </div>
  );
}

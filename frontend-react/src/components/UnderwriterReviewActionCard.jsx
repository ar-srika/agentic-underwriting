import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, XCircle, FileSignature, Lock } from 'lucide-react';

export default function UnderwriterReviewActionCard({ decision, onOverrideDecision, selectedRole = 'Senior Underwriter' }) {
  const [comments, setComments] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!decision || (!decision.requires_human_review && decision.decision !== 'Manual Review Required' && decision.decision !== 'Underwriter Approved' && decision.decision !== 'Underwriter Declined')) {
    return null;
  }

  const isAlreadyReviewed = decision.decision === 'Underwriter Approved' || decision.decision === 'Underwriter Declined';
  const hasBindingAuthority = selectedRole === 'Senior Underwriter';

  const handleAction = async (decisionType) => {
    setIsSubmitting(true);
    try {
      await onOverrideDecision({
        submissionId: decision.submission_id,
        decisionType: decisionType,
        comments: comments || (decisionType === 'APPROVED' ? `Approved by ${selectedRole}` : `Declined by ${selectedRole}`),
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        background: isAlreadyReviewed
          ? decision.decision === 'Underwriter Approved' ? '#f0fdf4' : '#fef2f2'
          : '#fffbeb',
        border: `1px solid ${
          isAlreadyReviewed
            ? decision.decision === 'Underwriter Approved' ? '#bbf7d0' : '#fecaca'
            : '#fde68a'
        }`,
        borderRadius: '12px',
        padding: '18px 20px',
        marginBottom: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileSignature size={20} color={isAlreadyReviewed ? (decision.decision === 'Underwriter Approved' ? '#15803d' : '#b91c1c') : '#b45309'} />
          <span style={{ fontSize: '1rem', fontWeight: 800, color: isAlreadyReviewed ? (decision.decision === 'Underwriter Approved' ? '#15803d' : '#b91c1c') : '#92400e', fontFamily: 'Outfit, sans-serif' }}>
            {isAlreadyReviewed
              ? decision.decision === 'Underwriter Approved'
                ? '✅ Underwriter Decision: Bound & Approved'
                : '🚫 Underwriter Decision: Formally Declined'
              : '👨‍💼 Action Required: Senior Underwriter Review Desk'}
          </span>
        </div>

        <span
          style={{
            background: isAlreadyReviewed ? '#ffffff' : '#fef3c7',
            color: isAlreadyReviewed ? '#15803d' : '#b45309',
            fontSize: '0.75rem',
            fontWeight: 700,
            padding: '3px 10px',
            borderRadius: '12px',
            border: '1px solid currentColor'
          }}
        >
          Priority: {decision.review_priority || 'Critical'}
        </span>
      </div>

      {!isAlreadyReviewed ? (
        <>
          <div style={{ fontSize: '0.8rem', color: '#78350f', marginBottom: '12px', lineHeight: '1.5' }}>
            {decision.reviewer_notifications && decision.reviewer_notifications.length > 0 ? (
              decision.reviewer_notifications.map((n, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                  <span>⚠️</span>
                  <span>{n}</span>
                </div>
              ))
            ) : (
              <div>• Natural hazard zone detected (FEMA SFHA / Hurricane Tier) or score within review threshold.</div>
            )}
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#92400e', marginBottom: '4px' }}>
              ✍️ Endorsement Comments & Rationale ({selectedRole}):
            </label>
            <textarea
              className="form-textarea"
              style={{ minHeight: '75px', background: '#ffffff', fontSize: '0.8rem' }}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Add optional notes: e.g. 'Approved with 5% coastal windstorm deductible endorsement'..."
            />
          </div>

          {hasBindingAuthority ? (
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                type="button"
                className="submit-btn"
                style={{
                  background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
                  boxShadow: '0 2px 8px rgba(22, 163, 74, 0.3)',
                  flex: 1,
                  fontSize: '0.85rem',
                  padding: '10px 14px'
                }}
                onClick={() => handleAction('APPROVED')}
                disabled={isSubmitting}
              >
                <CheckCircle2 size={16} />
                <span>✅ Approve & Bind Policy (as Senior Underwriter)</span>
              </button>

              <button
                type="button"
                className="submit-btn"
                style={{
                  background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
                  boxShadow: '0 2px 8px rgba(220, 38, 38, 0.3)',
                  flex: 1,
                  fontSize: '0.85rem',
                  padding: '10px 14px'
                }}
                onClick={() => handleAction('DECLINED')}
                disabled={isSubmitting}
              >
                <XCircle size={16} />
                <span>🚫 Decline Policy</span>
              </button>
            </div>
          ) : (
            <div style={{ background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '10px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#475569' }}>
                <Lock size={16} color="#64748b" />
                <span>
                  <b>Binding Authority Restricted:</b> Switch active persona to <b>Senior Underwriter</b> in the top right to bind coverage.
                </span>
              </div>
              <button
                type="button"
                className="gov-badge"
                style={{ cursor: 'pointer', background: '#eff6ff', borderColor: '#bfdbfe', color: '#1d4ed8' }}
                onClick={() => handleAction('ADVISORY')}
              >
                Log Advisory Comment
              </button>
            </div>
          )}
        </>
      ) : (
        <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '6px' }}>
          <div><b>Reviewer Comments:</b> {decision.underwriter_comments || 'Underwriter review recorded.'}</div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
            Snapshot committed to 90-day cold-storage Memory Bank.
          </div>
        </div>
      )}
    </div>
  );
}

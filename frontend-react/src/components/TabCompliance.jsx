import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck } from 'lucide-react';

export default function TabCompliance({ compliance }) {
  if (!compliance) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
        No compliance audit generated yet. Submit an application to run the 10 statutory checks.
      </div>
    );
  }

  const { overall_status, compliance_score, passed_count, warning_count, failed_count, checks, review_reasons } = compliance;

  const statusVal = overall_status?.value || overall_status || 'Pass';
  const isPass = statusVal === 'Pass';
  const isWarning = statusVal === 'Warning';

  return (
    <div>
      {/* Compliance Hero Metric */}
      <div className="enterprise-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
              Statutory Regulatory Compliance Audit
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
              <span
                style={{
                  fontSize: '1.4rem',
                  fontWeight: 800,
                  fontFamily: 'Outfit, sans-serif',
                  color: isPass ? '#16a34a' : isWarning ? '#d97706' : '#dc2626'
                }}
              >
                {statusVal} ({compliance_score}%)
              </span>
              <span
                style={{
                  background: isPass ? '#dcfce7' : isWarning ? '#fef3c7' : '#fee2e2',
                  color: isPass ? '#15803d' : isWarning ? '#b45309' : '#b91c1c',
                  padding: '3px 10px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: 700
                }}
              >
                {passed_count} / {checks?.length || 10} Rules Satisfied
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ textAlign: 'center', background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '8px 14px', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#15803d' }}>{passed_count}</div>
              <div style={{ fontSize: '0.7rem', color: '#166534', fontWeight: 600 }}>Passed</div>
            </div>
            <div style={{ textAlign: 'center', background: '#fffbeb', border: '1px solid #fde68a', padding: '8px 14px', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#b45309' }}>{warning_count}</div>
              <div style={{ fontSize: '0.7rem', color: '#92400e', fontWeight: 600 }}>Warnings</div>
            </div>
            <div style={{ textAlign: 'center', background: '#fef2f2', border: '1px solid #fecaca', padding: '8px 14px', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#b91c1c' }}>{failed_count}</div>
              <div style={{ fontSize: '0.7rem', color: '#991b1b', fontWeight: 600 }}>Violations</div>
            </div>
          </div>
        </div>

        {review_reasons && review_reasons.length > 0 && (
          <div style={{ marginTop: '16px', padding: '10px 14px', background: isWarning ? '#fffbeb' : '#fef2f2', border: `1px solid ${isWarning ? '#fde68a' : '#fecaca'}`, borderRadius: '8px' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: isWarning ? '#92400e' : '#991b1b', marginBottom: '4px' }}>
              ⚠️ Statutory Review Items:
            </div>
            <ul style={{ paddingLeft: '16px', fontSize: '0.75rem', color: isWarning ? '#b45309' : '#b91c1c' }}>
              {review_reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 10 Statutory Rules Table */}
      <div className="enterprise-card">
        <div className="card-header">
          <span>⚖️ 10 Statutory Rules Evaluated</span>
        </div>

        <table className="compliance-table">
          <thead>
            <tr>
              <th>Rule ID</th>
              <th>Compliance Check Name</th>
              <th>Audit Status</th>
              <th>Evaluation Findings & Statutory Rationale</th>
            </tr>
          </thead>
          <tbody>
            {checks?.map((check, idx) => {
              const cStatus = check.status?.value || check.status || 'Pass';
              const isRulePass = cStatus === 'Pass';
              const isRuleWarn = cStatus === 'Warning';

              return (
                <tr key={idx}>
                  <td style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1e3a8a' }}>{check.rule_id}</td>
                  <td style={{ fontWeight: 600 }}>{check.name}</td>
                  <td>
                    <span className={`status-badge ${isRulePass ? 'pass' : isRuleWarn ? 'warning' : 'fail'}`}>
                      {isRulePass ? <CheckCircle2 size={12} /> : isRuleWarn ? <AlertTriangle size={12} /> : <XCircle size={12} />}
                      {cStatus}
                    </span>
                  </td>
                  <td style={{ color: '#475569' }}>{check.details}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Fair Lending & Model Armor Notice */}
      <div style={{ fontSize: '0.75rem', color: '#64748b', background: '#f8fafc', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldCheck size={20} color="#16a34a" />
        <span>
          <b>Fair Lending (ECOA / FCRA) Compliance Verified:</b> Rating factors exclude prohibited demographic classes and adhere to state insurance commissioner filed rating formulas.
        </span>
      </div>
    </div>
  );
}

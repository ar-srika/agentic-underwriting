import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, ShieldCheck, AlertTriangle, XCircle, DollarSign, Clock, RefreshCw, Eye } from 'lucide-react';

export default function TabPortfolioAnalytics({ onSelectSubmission }) {
  const [stats, setStats] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, subsRes] = await Promise.all([
        fetch('/api/v1/metrics'),
        fetch('/api/v1/submissions'),
      ]);

      if (statsRes.ok) {
        const sData = await statsRes.json();
        setStats(sData);
      }
      if (subsRes.ok) {
        const subData = await subsRes.json();
        setSubmissions(subData);
      }
    } catch (e) {
      console.error('Failed to load portfolio analytics:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const total = stats?.total_submissions || submissions.length || 0;
  const approved = (stats?.auto_approved || 0) + (stats?.underwriter_approved || 0);
  const manual = stats?.manual_review || 0;
  const declined = (stats?.auto_declined || 0) + (stats?.underwriter_declined || 0);
  const avgPrem = stats?.avg_premium || 0;
  const avgRisk = stats?.avg_risk_score || 0;

  return (
    <div>
      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '14px', marginBottom: '20px' }}>
        <div className="enterprise-card" style={{ marginBottom: 0, padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>Total Submissions</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: '#0f172a', marginTop: '2px' }}>
            {total}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#16a34a', fontWeight: 600 }}>Active Portfolio Fleet</div>
        </div>

        <div className="enterprise-card" style={{ marginBottom: 0, padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: '#15803d', fontWeight: 600 }}>Auto-Approved / Bound</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: '#16a34a', marginTop: '2px' }}>
            {approved}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
            {total > 0 ? `${((approved / total) * 100).toFixed(0)}% straight-through` : '0%'}
          </div>
        </div>

        <div className="enterprise-card" style={{ marginBottom: 0, padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: '#b45309', fontWeight: 600 }}>Manual Review Required</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: '#d97706', marginTop: '2px' }}>
            {manual}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Senior Underwriter Queue</div>
        </div>

        <div className="enterprise-card" style={{ marginBottom: 0, padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: '#b91c1c', fontWeight: 600 }}>Auto-Declined</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: '#dc2626', marginTop: '2px' }}>
            {declined}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Policy / Class Exclusion</div>
        </div>

        <div className="enterprise-card" style={{ marginBottom: 0, padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: '#1d4ed8', fontWeight: 600 }}>Average Bound Premium</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: '#1976d2', marginTop: '2px' }}>
            ${avgPrem > 0 ? avgPrem.toLocaleString(undefined, { maximumFractionDigits: 0 }) : '—'}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Avg Risk: {avgRisk}/100</div>
        </div>
      </div>

      {/* Submissions History Table */}
      <div className="enterprise-card">
        <div className="card-header">
          <div className="card-header-left">
            <BarChart3 size={18} color="#1976d2" />
            <span>📈 Portfolio Submissions Ledger & Historical Audit</span>
          </div>
          <button
            type="button"
            className="gov-badge"
            style={{ cursor: 'pointer' }}
            onClick={loadData}
          >
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            <span>Refresh Ledger</span>
          </button>
        </div>

        {submissions.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
            No underwriting decisions stored in memory yet. Run an assessment to log submissions.
          </div>
        ) : (
          <table className="compliance-table">
            <thead>
              <tr>
                <th>Submission ID</th>
                <th>Business Name & City</th>
                <th>Decision Status</th>
                <th>Risk Score</th>
                <th>Final Premium</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub, idx) => {
                const dec = sub.decision;
                const isApp = dec === 'Auto-Approved' || dec === 'Underwriter Approved';
                const isWarn = dec === 'Manual Review Required';
                const bizName = sub.submission_data?.business_info?.business_name || 'Commercial Applicant';
                const city = sub.submission_data?.property_details?.city || sub.submission_data?.property_details?.state || 'US';
                const prem = sub.pricing?.final_premium;

                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1e3a8a' }}>
                      {sub.submission_id}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{bizName}</div>
                      <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{city} · {sub.submission_data?.business_info?.business_type || 'General'}</div>
                    </td>
                    <td>
                      <span className={`status-badge ${isApp ? 'pass' : isWarn ? 'warning' : 'fail'}`}>
                        {dec}
                      </span>
                    </td>
                    <td style={{ fontWeight: 700 }}>
                      {sub.risk_profile?.composite_score ?? '—'}/100
                    </td>
                    <td style={{ fontWeight: 700, color: '#1976d2' }}>
                      {prem ? `$${prem.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {sub.created_at ? new Date(sub.created_at).toLocaleTimeString() : 'Just now'}
                    </td>
                    <td>
                      {onSelectSubmission && (
                        <button
                          type="button"
                          className="gov-badge"
                          style={{ cursor: 'pointer', background: '#eff6ff', borderColor: '#bfdbfe', color: '#1d4ed8' }}
                          onClick={() => onSelectSubmission(sub)}
                          title="Load this submission into the active workspace"
                        >
                          <Eye size={12} />
                          <span>View</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

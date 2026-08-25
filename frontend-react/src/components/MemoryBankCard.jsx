import React, { useState, useEffect } from 'react';
import { Database, RefreshCw, Clock, CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';

export default function MemoryBankCard({ onHydrateSession }) {
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hydratedId, setHydratedId] = useState(null);

  const fetchSnapshots = async () => {
    try {
      const res = await fetch('/api/v1/sessions');
      if (res.ok) {
        const data = await res.json();
        setSnapshots(data);
      }
    } catch (e) {
      console.error('Failed to fetch session snapshots:', e);
    }
  };

  useEffect(() => {
    fetchSnapshots();
  }, []);

  const handleHydrate = async (sessionId) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/sessions/${sessionId}/hydrate`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setHydratedId(sessionId);
        if (onHydrateSession && data.snapshot?.decision) {
          onHydrateSession(data.snapshot.decision);
        }
        await fetchSnapshots();
      }
    } catch (e) {
      console.error('Failed to re-hydrate session:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="enterprise-card" style={{ marginTop: '20px', border: '1px solid #cbd5e1' }}>
      <div className="card-header" style={{ background: '#f1f5f9' }}>
        <div className="card-header-left">
          <Database size={18} color="#0f766e" />
          <span style={{ color: '#0f172a', fontWeight: 700 }}>
            🧠 Enterprise Memory Bank & Asynchronous Runtime (90-Day TTL Cold Storage)
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#0f766e', background: '#ccfbf1', padding: '2px 8px', borderRadius: '10px' }}>
            Sovereign Region: us-central1
          </span>
          <button
            type="button"
            className="icon-btn"
            style={{ padding: '4px', border: 'none', background: 'transparent', cursor: 'pointer' }}
            onClick={fetchSnapshots}
            title="Refresh Snapshots"
          >
            <RefreshCw size={14} color="#64748b" />
          </button>
        </div>
      </div>

      <div style={{ padding: '16px' }}>
        <div style={{ fontSize: '0.8rem', color: '#475569', marginBottom: '14px', lineHeight: '1.5' }}>
          Enables multi-week asynchronous operations. When an intake or site survey requires days/weeks of offline processing, the complete agent execution state, OTel trace IDs, and risk profile are safely preserved in cold storage without context loss.
        </div>

        {snapshots.length === 0 ? (
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', textAlign: 'center', padding: '16px' }}>
            No cold-storage session snapshots currently queued. Run an underwriting assessment to persist a session.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="enterprise-table" style={{ width: '100%', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ background: '#f8fafc', textAlign: 'left', borderBottom: '1px solid #e2e8f0' }}>
                  <th style={{ padding: '8px 12px' }}>Snapshot ID</th>
                  <th style={{ padding: '8px 12px' }}>Applicant Business</th>
                  <th style={{ padding: '8px 12px' }}>Age / Retention</th>
                  <th style={{ padding: '8px 12px' }}>Lifecycle Status</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Asynchronous State Action</th>
                </tr>
              </thead>
              <tbody>
                {snapshots.map((snap) => {
                  const bizName = snap.decision?.submission_data?.business_info?.business_name || snap.submission_id || 'Commercial Applicant';
                  const isHist = snap.session_id.includes('WK2') || snap.created_at?.includes('202') && snap.session_id.startsWith('SNAP-WK');
                  const isHydrated = hydratedId === snap.session_id || snap.status === 'HYDRATED';

                  return (
                    <tr key={snap.session_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '10px 12px', fontWeight: 700, color: '#1e293b' }}>
                        <code>{snap.session_id}</code>
                      </td>
                      <td style={{ padding: '10px 12px', color: '#334155' }}>
                        <div><b>{bizName}</b></div>
                        <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Sub-ID: {snap.submission_id}</div>
                      </td>
                      <td style={{ padding: '10px 12px', color: '#475569' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={13} color="#64748b" />
                          <span>{isHist ? '14 days ago (Week 2 Hold)' : 'Active Session'}</span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: '#0f766e' }}>90-Day TTL Window</div>
                      </td>
                      <td style={{ padding: '10px 12px' }}>
                        <span
                          style={{
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '6px',
                            background: isHydrated ? '#dcfce7' : snap.status === 'PENDING_REVIEW' ? '#fef3c7' : '#e0f2fe',
                            color: isHydrated ? '#15803d' : snap.status === 'PENDING_REVIEW' ? '#b45309' : '#0369a1',
                          }}
                        >
                          {isHydrated ? '⚡ RE-HYDRATED (ACTIVE)' : snap.status}
                        </span>
                      </td>
                      <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                        <button
                          type="button"
                          className="btn-secondary"
                          style={{
                            fontSize: '0.75rem',
                            padding: '4px 10px',
                            background: isHydrated ? '#f0fdf4' : '#0f766e',
                            color: isHydrated ? '#16a34a' : '#ffffff',
                            border: isHydrated ? '1px solid #86efac' : 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontWeight: 600,
                          }}
                          onClick={() => handleHydrate(snap.session_id)}
                          disabled={loading}
                        >
                          {isHydrated ? (
                            <>
                              <CheckCircle2 size={13} />
                              <span>Hydrated</span>
                            </>
                          ) : (
                            <>
                              <span>⚡ Re-Hydrate Context</span>
                              <ArrowRight size={13} />
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

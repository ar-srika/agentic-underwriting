import React, { useState, useEffect } from 'react';
import { Users, Shield, Server, CheckCircle2 } from 'lucide-react';

export default function TabRegistry() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/registry')
      .then((res) => res.json())
      .then((data) => {
        setAgents(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load agent registry:', err);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="enterprise-card">
        <div className="card-header">
          <div className="card-header-left">
            <Server size={18} color="#1976d2" />
            <span>📋 Enterprise Agent & Sub-Agent Catalog</span>
          </div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#16a34a' }}>
            {agents.length} Registered Autonomous Units
          </span>
        </div>

        <table className="compliance-table">
          <thead>
            <tr>
              <th>Agent ID</th>
              <th>Name & Purpose</th>
              <th>Version</th>
              <th>Authorized Departments</th>
              <th>Health</th>
            </tr>
          </thead>
          <tbody>
            {agents.map((a, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1e3a8a' }}>{a.agent_id}</td>
                <td>
                  <div style={{ fontWeight: 600 }}>{a.agent_name}</div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{a.description}</div>
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{a.version}</td>
                <td>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {a.authorized_departments?.map((dept, di) => (
                      <span
                        key={di}
                        style={{
                          background: '#f1f5f9',
                          color: '#475569',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '0.7rem',
                          fontWeight: 600
                        }}
                      >
                        {dept}
                      </span>
                    ))}
                  </div>
                </td>
                <td>
                  <span className="status-badge pass">
                    <CheckCircle2 size={12} />
                    {a.health || 'Healthy'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

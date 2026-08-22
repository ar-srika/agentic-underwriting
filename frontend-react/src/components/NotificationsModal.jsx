import React, { useState, useEffect } from 'react';
import { X, Bell, AlertTriangle, Info, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function NotificationsModal({ isOpen, onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/notifications');
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (e) {
      console.error('Failed to load notifications:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: '650px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={20} color="#1976d2" />
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
              🔔 Senior Underwriter Notification Alert Center
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {notifications.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
            <CheckCircle2 size={36} color="#16a34a" style={{ margin: '0 auto 8px' }} />
            <div style={{ fontWeight: 700, color: '#1e293b' }}>All Clear! No Pending Review Notifications</div>
            <div style={{ fontSize: '0.75rem', marginTop: '4px' }}>Submissions requiring human underwriter review will appear here.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {notifications.map((n, idx) => {
              const sev = n.severity?.toUpperCase() || 'INFO';
              const isCrit = sev === 'CRITICAL' || sev === 'HIGH';
              const isWarn = sev === 'WARNING' || sev === 'MEDIUM';

              return (
                <div
                  key={idx}
                  style={{
                    background: isCrit ? '#fef2f2' : isWarn ? '#fffbeb' : '#f0fdf4',
                    border: `1px solid ${isCrit ? '#fecaca' : isWarn ? '#fde68a' : '#bbf7d0'}`,
                    borderRadius: '8px',
                    padding: '12px 14px',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px'
                  }}
                >
                  {isCrit ? (
                    <ShieldAlert size={20} color="#dc2626" style={{ flexShrink: 0, marginTop: '2px' }} />
                  ) : isWarn ? (
                    <AlertTriangle size={20} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
                  ) : (
                    <Info size={20} color="#16a34a" style={{ flexShrink: 0, marginTop: '2px' }} />
                  )}

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: isCrit ? '#991b1b' : isWarn ? '#92400e' : '#166534' }}>
                        {n.title || `Alert: ${sev}`}
                      </span>
                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
                        {n.timestamp ? new Date(n.timestamp).toLocaleTimeString() : 'Just now'}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '4px' }}>
                      {n.message}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div style={{ marginTop: '16px', textAlign: 'right' }}>
          <button
            type="button"
            className="submit-btn"
            style={{ padding: '6px 16px', fontSize: '0.8rem', width: 'auto', display: 'inline-flex' }}
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import { X, Home, BarChart3, Activity, Users, Bell, ShieldCheck, RotateCcw, Building2, Trash2 } from 'lucide-react';

export default function SidebarDrawer({
  isOpen,
  onClose,
  currentView,
  onSelectView,
  notificationsCount = 0,
  onOpenNotifications,
  onClearCache,
}) {
  if (!isOpen) return null;

  const menuItems = [
    {
      id: 'workspace',
      title: 'Active Underwriting Workspace',
      desc: 'Assess ACORD applications & real-time rating',
      icon: <Home size={18} color="#1976d2" />,
      badge: 'Live',
      badgeColor: '#dcfce7',
      badgeText: '#15803d',
    },
    {
      id: 'analytics',
      title: 'Portfolio Analytics & History',
      desc: 'All status history, KPIs & submissions records',
      icon: <BarChart3 size={18} color="#0284c7" />,
      badge: 'Analytics',
      badgeColor: '#e0f2fe',
      badgeText: '#0369a1',
    },
    {
      id: 'audit',
      title: 'Audit Trail & OTel Telemetry',
      desc: 'Distributed trace spans & Model Armor ZDR logs',
      icon: <Activity size={18} color="#7c3aed" />,
      badge: 'Observability',
      badgeColor: '#faf5ff',
      badgeText: '#6b21a8',
    },
    {
      id: 'registry',
      title: 'Agent Registry & RBAC',
      desc: 'Catalog of 10 registered autonomous units',
      icon: <Users size={18} color="#ea580c" />,
      badge: '10 Agents',
      badgeColor: '#fff7ed',
      badgeText: '#c2410c',
    },
  ];

  const handleItemClick = (id) => {
    onSelectView(id);
    onClose();
  };

  const handleClearCacheClick = () => {
    onClearCache();
    onClose();
  };

  return (
    <div className="sidebar-overlay" onClick={onClose}>
      <div className="sidebar-drawer" onClick={(e) => e.stopPropagation()}>
        {/* Sidebar Header */}
        <div className="sidebar-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div className="brand-icon" style={{ width: '32px', height: '32px', fontSize: '1rem' }}>
              <Building2 size={18} />
            </div>
            <div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
                Platform Navigation
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                Enterprise Underwriting Suite
              </div>
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Sidebar Menu Items */}
        <div className="sidebar-content">
          <div className="sidebar-section-label">📌 Platform Modules:</div>

          {menuItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`sidebar-menu-btn ${currentView === item.id ? 'active' : ''}`}
              onClick={() => handleItemClick(item.id)}
            >
              <div className="sidebar-menu-left">
                {item.icon}
                <div style={{ textAlign: 'left' }}>
                  <div>{item.title}</div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: 400 }}>{item.desc}</div>
                </div>
              </div>
              <span
                style={{
                  background: item.badgeColor,
                  color: item.badgeText,
                  padding: '2px 6px',
                  borderRadius: '10px',
                  fontSize: '0.65rem',
                  fontWeight: 700
                }}
              >
                {item.badge}
              </span>
            </button>
          ))}

          <div className="sidebar-section-label" style={{ marginTop: '20px' }}>🔔 Underwriter Alerts:</div>

          <button
            type="button"
            className="sidebar-menu-btn"
            onClick={() => {
              onClose();
              onOpenNotifications();
            }}
          >
            <div className="sidebar-menu-left">
              <Bell size={18} color="#ea580c" />
              <div style={{ textAlign: 'left' }}>
                <div>Notification Alert Center</div>
                <div style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: 400 }}>
                  Review required alerts & notices
                </div>
              </div>
            </div>
            {notificationsCount > 0 && (
              <span
                style={{
                  background: '#fef2f2',
                  color: '#dc2626',
                  padding: '2px 8px',
                  borderRadius: '10px',
                  fontSize: '0.7rem',
                  fontWeight: 800
                }}
              >
                {notificationsCount} New
              </span>
            )}
          </button>

          <div className="sidebar-section-label" style={{ marginTop: '20px' }}>⚙️ Session Management:</div>

          {/* Clear Cache & Reset Button */}
          <button
            type="button"
            className="sidebar-menu-btn"
            style={{ color: '#b91c1c' }}
            onClick={handleClearCacheClick}
          >
            <div className="sidebar-menu-left">
              <RotateCcw size={18} color="#dc2626" />
              <div style={{ textAlign: 'left' }}>
                <div style={{ color: '#dc2626', fontWeight: 700 }}>Clear Cache & Reset</div>
                <div style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: 400 }}>
                  Clear decision, input, and notifications
                </div>
              </div>
            </div>
            <span
              style={{
                background: '#fef2f2',
                color: '#dc2626',
                padding: '2px 6px',
                borderRadius: '10px',
                fontSize: '0.65rem',
                fontWeight: 700
              }}
            >
              Reset
            </span>
          </button>
        </div>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#15803d', fontWeight: 600 }}>
            <ShieldCheck size={16} />
            <span>Zero-Data-Retention Sovereign Cloud</span>
          </div>
          <div style={{ marginTop: '2px', fontSize: '0.7rem', color: '#94a3b8' }}>
            Tenant #8820 · Google Cloud us-central1
          </div>
        </div>
      </div>
    </div>
  );
}

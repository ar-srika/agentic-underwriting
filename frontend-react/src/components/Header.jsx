import React from 'react';
import { ShieldCheck, Cloud, Cpu, Building2, UserCheck, Bell, Menu } from 'lucide-react';

export default function Header({
  selectedRole,
  onRoleChange,
  unreadNotificationsCount = 0,
  onOpenNotifications,
  onToggleSidebar,
}) {
  return (
    <header className="enterprise-header">
      <div className="header-inner">
        <div className="header-brand">
          {/* Hamburger Menu Button */}
          <button
            type="button"
            className="hamburger-btn"
            onClick={onToggleSidebar}
            title="Open Platform Navigation Menu (Portfolio Analytics, Audit Trail, Agent Registry, Clear Cache)"
          >
            <Menu size={20} />
          </button>

          <div className="brand-icon">
            <Building2 size={22} />
          </div>

          <div>
            <div className="brand-title">
              UnderwriteAI
              <span style={{ fontSize: '0.72rem', fontWeight: 600, background: '#eff6ff', color: '#1d4ed8', padding: '2px 8px', borderRadius: '12px', border: '1px solid #bfdbfe' }}>
                Enterprise Intelligence Platform
              </span>
            </div>
            <div className="brand-subtitle">
              Multi-Agent AI Platform for Small Business Insurance Underwriting
            </div>
          </div>
        </div>

        <div className="header-badges">
          <div className="gov-badge active">
            <Cloud size={14} />
            <span>US-Central1 (Iowa)</span>
          </div>

          <div className="gov-badge armor">
            <ShieldCheck size={14} />
            <span>Model Armor: Active (ZDR)</span>
          </div>

          <div className="gov-badge">
            <Cpu size={14} />
            <span>Gemini 3.5 Pro</span>
          </div>

          {/* Notifications Trigger */}
          <button
            type="button"
            className="gov-badge"
            style={{
              cursor: 'pointer',
              background: unreadNotificationsCount > 0 ? '#fffbeb' : '#f8fafc',
              borderColor: unreadNotificationsCount > 0 ? '#fde68a' : '#e2e8f0',
              color: unreadNotificationsCount > 0 ? '#b45309' : '#64748b'
            }}
            onClick={onOpenNotifications}
            title="View Underwriter Notifications"
          >
            <Bell size={14} />
            <span>Notifications</span>
            {unreadNotificationsCount > 0 && (
              <span style={{ background: '#ea580c', color: '#ffffff', borderRadius: '10px', padding: '1px 6px', fontSize: '0.65rem', fontWeight: 800 }}>
                {unreadNotificationsCount}
              </span>
            )}
          </button>

          {/* Role Dropdown in Top Right */}
          <div className="rbac-selector">
            <UserCheck size={14} />
            <span>Role:</span>
            <select
              className="rbac-select"
              value={selectedRole}
              onChange={(e) => onRoleChange(e.target.value)}
            >
              <option value="Senior Underwriter">Senior Underwriter</option>
              <option value="Actuary">Actuary</option>
              <option value="Compliance Officer">Compliance Officer</option>
              <option value="Claims Adjuster">Claims Adjuster</option>
              <option value="Broker API Client">Broker API Client</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
}

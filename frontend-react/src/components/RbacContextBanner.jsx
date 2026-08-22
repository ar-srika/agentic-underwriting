import React from 'react';
import { UserCheck, Shield, CheckCircle2, Lock } from 'lucide-react';

export default function RbacContextBanner({ selectedRole }) {
  const roleConfig = {
    'Senior Underwriter': {
      color: '#1e3a8a',
      bg: '#eff6ff',
      border: '#bfdbfe',
      icon: '👨‍💼',
      authority: 'Tier 3 Commercial Binding Authority ($1,000,000 Limit)',
      badge: 'Full Binding Access',
      badgeBg: '#dcfce7',
      badgeColor: '#15803d',
      desc: 'You have full authorization to override risk flags, endorse policies, and bind commercial coverage.',
    },
    'Actuary': {
      color: '#0369a1',
      bg: '#f0f9ff',
      border: '#bae6fd',
      icon: '📐',
      authority: 'Actuarial Quantitative Modeling & Rating Formula Audit',
      badge: 'Advisory Mode',
      badgeBg: '#fef3c7',
      badgeColor: '#b45309',
      desc: 'Authorized to inspect pricing multipliers, modifier formulas, and $10K policy cap bounds. Binding is reserved for Underwriters.',
    },
    'Compliance Officer': {
      color: '#15803d',
      bg: '#f0fdf4',
      border: '#bbf7d0',
      icon: '⚖️',
      authority: 'Statutory Regulatory & Fair Lending (ECOA/FCRA) Enforcement',
      badge: 'Compliance Audit Mode',
      badgeBg: '#dbeafe',
      badgeColor: '#1d4ed8',
      desc: 'Authorized to audit all 10 statutory rules, prohibited industry classes, and environmental disclosures.',
    },
    'Claims Adjuster': {
      color: '#b45309',
      bg: '#fffbeb',
      border: '#fde68a',
      icon: '📉',
      authority: 'Loss Experience & Prior Claims History Verification',
      badge: 'Claims Analysis Mode',
      badgeBg: '#ffedd5',
      badgeColor: '#c2410c',
      desc: 'Authorized to inspect past 3-year loss runs, fraud indicators, and severe weather vulnerability.',
    },
    'Broker API Client': {
      color: '#6b21a8',
      bg: '#faf5ff',
      border: '#e9d5ff',
      icon: '🏢',
      authority: 'External Broker Portal (Quoting & Intake Only)',
      badge: 'Broker Quoting View',
      badgeBg: '#f3e8ff',
      badgeColor: '#7e22ce',
      desc: 'External broker view: Submit ACORD applications, view real-time quoting estimates, and track submission status.',
    },
  };

  const config = roleConfig[selectedRole] || roleConfig['Senior Underwriter'];

  return (
    <div
      style={{
        background: config.bg,
        border: `1px solid ${config.border}`,
        borderRadius: '8px',
        padding: '8px 16px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ fontSize: '1.2rem' }}>{config.icon}</span>
        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: config.color }}>
            Active RBAC Persona: {selectedRole} · <span style={{ fontWeight: 500 }}>{config.authority}</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: '#475569' }}>
            {config.desc}
          </div>
        </div>
      </div>

      <span
        style={{
          background: config.badgeBg,
          color: config.badgeColor,
          padding: '2px 8px',
          borderRadius: '10px',
          fontSize: '0.7rem',
          fontWeight: 700,
          border: '1px solid currentColor'
        }}
      >
        {config.badge}
      </span>
    </div>
  );
}

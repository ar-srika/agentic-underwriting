import React from 'react';
import { DollarSign, ShieldAlert, CheckCircle, Percent } from 'lucide-react';

export default function TabPricing({ pricing }) {
  if (!pricing) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
        No pricing recommendation generated yet. Submit an application to compute premium.
      </div>
    );
  }

  const {
    base_premium,
    modifier_product,
    calculated_premium,
    final_premium,
    premium_capped,
    product_recommendation,
    coverage_limit,
    deductible,
    pricing_modifiers,
  } = pricing;

  const capPercentage = Math.min(100, (final_premium / 10000) * 100);

  return (
    <div>
      {/* Hero Pricing Header */}
      <div className="pricing-metric-box">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontSize: '0.85rem', opacity: 0.8, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
              Recommended Product Package
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '2px' }}>
              {product_recommendation}
            </div>
            <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '4px' }}>
              Coverage Limit: <b>${coverage_limit?.toLocaleString()}</b> · Deductible: <b>${deductible?.toLocaleString()}</b>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.8, fontWeight: 600 }}>Final Bound Premium</div>
            <div className="pricing-final-amt">
              ${final_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {premium_capped ? (
              <span style={{ background: '#fef3c7', color: '#92400e', fontSize: '0.75rem', fontWeight: 700, padding: '3px 8px', borderRadius: '12px' }}>
                ⚠️ CAPPED at $10,000 Statutory Limit
              </span>
            ) : (
              <span style={{ background: '#dcfce7', color: '#15803d', fontSize: '0.75rem', fontWeight: 700, padding: '3px 8px', borderRadius: '12px' }}>
                ✅ Within Actuarial Ceiling
              </span>
            )}
          </div>
        </div>

        {/* $10K Cap Bar */}
        <div style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', opacity: 0.9, marginBottom: '4px' }}>
            <span>$500 Policy Floor</span>
            <span>Policy Cap Utilization ({capPercentage.toFixed(1)}%)</span>
            <span>$10,000 Max Policy Cap</span>
          </div>
          <div style={{ height: '8px', background: 'rgba(255,255,255,0.2)', borderRadius: '4px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${capPercentage}%`,
                background: premium_capped ? '#f59e0b' : '#38bdf8',
                borderRadius: '4px',
                transition: 'width 0.4s ease'
              }}
            />
          </div>
        </div>
      </div>

      {/* Actuarial Calculation Flow Card */}
      <div className="enterprise-card">
        <div className="card-header">
          <span>⚙️ Actuarial Base Rate × 9 Modifiers Equation</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
          <div style={{ background: '#f8fafc', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>1. Base Premium Tier</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginTop: '2px' }}>
              ${base_premium?.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Derived from property value</div>
          </div>

          <div style={{ background: '#f8fafc', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>2. Composite Rating Factor</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#1d4ed8', marginTop: '2px' }}>
              {modifier_product?.toFixed(4)}x
            </div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Product of 9 actuarial multipliers</div>
          </div>

          <div style={{ background: '#f8fafc', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>3. Raw Calculated Premium</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginTop: '2px' }}>
              ${calculated_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Base × Modifier product</div>
          </div>
        </div>

        {/* Modifiers Table */}
        <table className="modifiers-table">
          <thead>
            <tr>
              <th>Rating Factor</th>
              <th>Multiplier Value</th>
              <th>Actuarial Rationale & Policy Rule</th>
            </tr>
          </thead>
          <tbody>
            {pricing_modifiers?.map((m, idx) => {
              const val = m.value;
              let badgeClass = 'modifier-standard';
              if (val < 1.0) badgeClass = 'modifier-discount';
              else if (val > 1.0) badgeClass = 'modifier-surcharge';

              return (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{m.name}</td>
                  <td>
                    <span className={`modifier-badge ${badgeClass}`}>
                      {val.toFixed(2)}x {val < 1.0 ? '(Discount)' : val > 1.0 ? '(Surcharge)' : '(Neutral)'}
                    </span>
                  </td>
                  <td style={{ color: '#475569' }}>{m.description}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

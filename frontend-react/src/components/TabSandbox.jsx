import React, { useState } from 'react';
import { Sliders, RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function TabSandbox({ decision }) {
  if (!decision || !decision.submission_data) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
        Run an underwriting assessment first to initialize the interactive sandbox.
      </div>
    );
  }

  const origProp = decision.submission_data.property_details || {};
  const origRisk = decision.risk_profile || {};
  const origPricing = decision.pricing || {};

  const [buildingAge, setBuildingAge] = useState(origProp.building_age_years || 10);
  const [hasSprinklers, setHasSprinklers] = useState(origProp.has_sprinkler_system ?? true);
  const [hasFireAlarm, setHasFireAlarm] = useState(origProp.has_fire_alarm ?? true);
  const [hasSecurity, setHasSecurity] = useState(origProp.has_security_system ?? true);
  const [claimsCount, setClaimsCount] = useState(decision.submission_data.claims_history?.total_claims_3yr || 0);

  // Deterministic local recalculation matching Python risk_calculator and pricing_engine
  let simPropertyScore = 30;
  if (buildingAge > 50) simPropertyScore += 25;
  else if (buildingAge > 30) simPropertyScore += 15;
  else if (buildingAge > 10) simPropertyScore += 5;
  else simPropertyScore -= 10;

  const safetyCount = (hasSprinklers ? 1 : 0) + (hasFireAlarm ? 1 : 0) + (hasSecurity ? 1 : 0);
  if (safetyCount === 3) simPropertyScore -= 20;
  else if (safetyCount === 2) simPropertyScore -= 10;
  else if (safetyCount === 1) simPropertyScore -= 5;
  else simPropertyScore += 15;

  simPropertyScore = Math.max(0, Math.min(100, simPropertyScore));

  // Pricing Modifier simulation
  let safetyMod = 1.15;
  if (safetyCount === 3) safetyMod = 0.82;
  else if (safetyCount === 2) safetyMod = 0.90;
  else if (safetyCount === 1) safetyMod = 0.95;

  let ageMod = 1.00;
  if (buildingAge < 10) ageMod = 0.90;
  else if (buildingAge < 30) ageMod = 1.00;
  else if (buildingAge < 50) ageMod = 1.10;
  else ageMod = 1.25;

  let claimsMod = 0.85;
  if (claimsCount === 1) claimsMod = 1.00;
  else if (claimsCount === 2) claimsMod = 1.15;
  else if (claimsCount <= 4) claimsMod = 1.40;
  else claimsMod = 1.60;

  const basePrem = origPricing.base_premium || 1500;
  // Estimate other static modifiers
  const otherMods = (origPricing.modifier_product || 1.0) / (0.82 * 1.00 * 0.85); // approximate baseline
  const simModifierProduct = otherMods * safetyMod * ageMod * claimsMod;
  const simCalculated = basePrem * simModifierProduct;
  const simFinal = Math.min(10000, Math.max(500, simCalculated));
  const simCapped = simCalculated > 10000;

  return (
    <div className="enterprise-card">
      <div className="card-header">
        <div className="card-header-left">
          <Sliders size={18} color="#1976d2" />
          <span>⚡ Interactive What-If Risk & Actuarial Sandbox</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
          Simulate loss-control upgrades and physical improvements in real-time
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        {/* Controls Column */}
        <div>
          {/* Building Age Slider */}
          <div className="sandbox-control-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700 }}>
              <span>🏗️ Building Age</span>
              <span style={{ color: '#1976d2' }}>{buildingAge} years</span>
            </div>
            <div className="sandbox-slider-row">
              <input
                type="range"
                min="0"
                max="80"
                value={buildingAge}
                onChange={(e) => setBuildingAge(Number(e.target.value))}
                className="sandbox-slider"
              />
            </div>
          </div>

          {/* Safety Systems Toggles */}
          <div className="sandbox-control-card">
            <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>
              🛡️ Protective Fire & Security Systems
            </div>
            <div className="sandbox-toggle-row">
              <button
                type="button"
                className={`sandbox-toggle-btn ${hasSprinklers ? 'active' : ''}`}
                onClick={() => setHasSprinklers(!hasSprinklers)}
              >
                {hasSprinklers ? '✅' : '❌'} Sprinkler System
              </button>
              <button
                type="button"
                className={`sandbox-toggle-btn ${hasFireAlarm ? 'active' : ''}`}
                onClick={() => setHasFireAlarm(!hasFireAlarm)}
              >
                {hasFireAlarm ? '✅' : '❌'} Central Fire Alarm
              </button>
              <button
                type="button"
                className={`sandbox-toggle-btn ${hasSecurity ? 'active' : ''}`}
                onClick={() => setHasSecurity(!hasSecurity)}
              >
                {hasSecurity ? '✅' : '❌'} Burglar Alarm
              </button>
            </div>
          </div>

          {/* Claims History Slider */}
          <div className="sandbox-control-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700 }}>
              <span>📉 Past 3-Year Claims</span>
              <span style={{ color: claimsCount > 2 ? '#dc2626' : '#1976d2' }}>{claimsCount} claims</span>
            </div>
            <div className="sandbox-slider-row">
              <input
                type="range"
                min="0"
                max="6"
                value={claimsCount}
                onChange={(e) => setClaimsCount(Number(e.target.value))}
                className="sandbox-slider"
              />
            </div>
          </div>
        </div>

        {/* Dynamic Simulation Output Column */}
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '12px' }}>
              📊 Real-Time Actuarial Impact
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #e2e8f0', fontSize: '0.8rem' }}>
              <span style={{ color: '#64748b' }}>Simulated Property Risk Score:</span>
              <span style={{ fontWeight: 700, color: simPropertyScore <= 35 ? '#16a34a' : '#dc2626' }}>
                {simPropertyScore.toFixed(1)} / 100
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #e2e8f0', fontSize: '0.8rem' }}>
              <span style={{ color: '#64748b' }}>Safety Credit Multiplier:</span>
              <span style={{ fontWeight: 700, color: safetyMod < 1.0 ? '#16a34a' : '#ea580c' }}>
                {safetyMod.toFixed(2)}x
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #e2e8f0', fontSize: '0.8rem' }}>
              <span style={{ color: '#64748b' }}>Building Age Multiplier:</span>
              <span style={{ fontWeight: 700 }}>
                {ageMod.toFixed(2)}x
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #e2e8f0', fontSize: '0.8rem' }}>
              <span style={{ color: '#64748b' }}>Claims Experience Multiplier:</span>
              <span style={{ fontWeight: 700, color: claimsMod < 1.0 ? '#16a34a' : '#dc2626' }}>
                {claimsMod.toFixed(2)}x
              </span>
            </div>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '16px', marginTop: '16px' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>Simulated Final Bound Premium</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: '#1976d2' }}>
              ${simFinal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {simCapped ? (
              <span style={{ fontSize: '0.75rem', color: '#b45309', fontWeight: 700 }}>
                ⚠️ Capped at $10,000 policy limit
              </span>
            ) : (
              <span style={{ fontSize: '0.75rem', color: '#15803d', fontWeight: 700 }}>
                ✅ Within standard underwriting bounds
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

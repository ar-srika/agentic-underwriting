import React, { useState } from 'react';
import { Play, UploadCloud, FileText, ChevronDown } from 'lucide-react';
import { PRESETS } from '../data/presets';

export default function SubmissionPanel({
  rawText,
  onTextChange,
  onSubmit,
  isLoading,
  onSelectPreset,
  selectedPresetId,
}) {
  const [selectedTab, setSelectedTab] = useState('text');
  const [fileName, setFileName] = useState(null);

  const handleDropdownChange = (e) => {
    const val = e.target.value;
    const found = PRESETS.find((p) => p.id === val);
    if (found) {
      onSelectPreset(found);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        onTextChange(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="enterprise-card">
      <div className="card-header">
        <div className="card-header-left">
          <FileText size={18} color="#1976d2" />
          <span>📥 Commercial Submission Intake</span>
        </div>
      </div>

      {/* Scenario Dropdown */}
      <div className="form-group" style={{ marginBottom: '14px' }}>
        <label className="form-label">
          📋 Select Underwriting Scenario:
        </label>
        <select
          className="form-textarea"
          style={{
            minHeight: 'auto',
            padding: '10px 12px',
            fontSize: '0.85rem',
            fontWeight: 600,
            cursor: 'pointer',
            background: '#f8fafc',
            border: '1px solid #cbd5e1'
          }}
          value={selectedPresetId || ''}
          onChange={handleDropdownChange}
        >
          <option value="" disabled>-- Select a pre-built commercial scenario or enter custom text --</option>
          <option value="low_risk">1. Low-Risk Small Business (Auto-Approved — Austin, TX)</option>
          <option value="coastal_hazard">2. Hazard Zone - Flood & Hurricane (Manual Review — Miami Beach, FL)</option>
          <option value="prohibited">3. Prohibited Business Class (Auto-Declined — Houston, TX)</option>
          <option value="seismic_retail">4. Moderate Risk Retailer (Standard BOP — San Francisco, CA)</option>
        </select>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px' }}>
        <button
          type="button"
          onClick={() => setSelectedTab('text')}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '0.8rem',
            fontWeight: selectedTab === 'text' ? 700 : 500,
            color: selectedTab === 'text' ? '#1976d2' : '#64748b',
            cursor: 'pointer',
            borderBottom: selectedTab === 'text' ? '2px solid #1976d2' : 'none',
            paddingBottom: '4px'
          }}
        >
          📝 ACORD Application Data
        </button>
        <button
          type="button"
          onClick={() => setSelectedTab('upload')}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '0.8rem',
            fontWeight: selectedTab === 'upload' ? 700 : 500,
            color: selectedTab === 'upload' ? '#1976d2' : '#64748b',
            cursor: 'pointer',
            borderBottom: selectedTab === 'upload' ? '2px solid #1976d2' : 'none',
            paddingBottom: '4px'
          }}
        >
          📄 Upload PDF / ACORD Form
        </button>
      </div>

      {selectedTab === 'text' ? (
        <div className="form-group">
          <textarea
            className="form-textarea"
            value={rawText}
            onChange={(e) => onTextChange(e.target.value)}
            placeholder="Paste raw ACORD 125/126 form text, broker email, or loss summary..."
          />
        </div>
      ) : (
        <div className="form-group" style={{ textAlign: 'center', padding: '24px 12px', background: '#f8fafc', border: '2px dashed #cbd5e1', borderRadius: '10px' }}>
          <UploadCloud size={32} color="#64748b" style={{ margin: '0 auto 8px' }} />
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
            {fileName ? `Selected: ${fileName}` : 'Drag and drop ACORD PDF or Broker Submission'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
            Supports PDF, TXT, CSV (up to 10MB)
          </div>
          <input
            type="file"
            accept=".pdf,.txt,.doc,.docx"
            onChange={handleFileChange}
            style={{ marginTop: '12px', fontSize: '0.75rem' }}
          />
        </div>
      )}

      <button
        type="button"
        className="submit-btn"
        onClick={onSubmit}
        disabled={isLoading || !rawText.trim()}
      >
        {isLoading ? (
          <>
            <span className="spinner" style={{ display: 'inline-block', width: '16px', height: '16px', border: '2px solid #ffffff', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
            <span>Orchestrating 6 Autonomous Agents...</span>
          </>
        ) : (
          <>
            <Play size={16} />
            <span>🚀 Begin Underwriting Assessment</span>
          </>
        )}
      </button>

      <div style={{ fontSize: '0.7rem', color: '#64748b', textAlign: 'center', marginTop: '10px' }}>
        ⚡ Model Armor zero-retention policy active · Regional Lock: US-Central1 (Iowa)
      </div>
    </div>
  );
}

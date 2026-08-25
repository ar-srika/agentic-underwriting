import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SidebarDrawer from './components/SidebarDrawer';
import SubmissionPanel from './components/SubmissionPanel';
import PipelineVisualizer from './components/PipelineVisualizer';
import DecisionBanner from './components/DecisionBanner';
import UnderwriterReviewActionCard from './components/UnderwriterReviewActionCard';
import LocationIntelligenceCard from './components/LocationIntelligenceCard';
import RbacContextBanner from './components/RbacContextBanner';
import AgentInspector from './components/AgentInspector';
import NotificationsModal from './components/NotificationsModal';
import TabRisk from './components/TabRisk';
import TabPricing from './components/TabPricing';
import TabCompliance from './components/TabCompliance';
import TabSandbox from './components/TabSandbox';
import TabReviewDesk from './components/TabReviewDesk';
import TabPortfolioAnalytics from './components/TabPortfolioAnalytics';
import TabAudit from './components/TabAudit';
import TabRegistry from './components/TabRegistry';
import TabMemoryBank from './components/TabMemoryBank';
import { PRESETS } from './data/presets';
import { ShieldCheck, Activity, Sliders, DollarSign, FileText, CheckCircle2, AlertTriangle, Users, BarChart3, ArrowLeft, Home } from 'lucide-react';

export default function App() {
  const [selectedRole, setSelectedRole] = useState('Senior Underwriter');
  const [selectedPresetId, setSelectedPresetId] = useState('low_risk');
  const [rawText, setRawText] = useState(PRESETS[0].text);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('risk');
  const [inspectedAgentId, setInspectedAgentId] = useState(null);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('workspace'); // 'workspace' | 'analytics' | 'audit' | 'registry'
  const [notificationsCount, setNotificationsCount] = useState(0);
  const [decision, setDecision] = useState(null); // Starts in ideal idle state
  const [cacheVersion, setCacheVersion] = useState(0); // Version tracker to force fresh load in isolated tabs

  const [pipelineStatus, setPipelineStatus] = useState({
    'intake-agent': 'idle',
    'risk-agent': 'idle',
    'pricing-agent': 'idle',
    'compliance-agent': 'idle',
    'orchestrator-agent': 'idle',
    'feedback-agent': 'idle',
  });

  const fetchNotificationCount = async () => {
    try {
      const res = await fetch('/api/v1/notifications');
      if (res.ok) {
        const notifs = await res.json();
        setNotificationsCount(notifs.length);
      }
    } catch (e) {
      // Ignore background fetch error
    }
  };

  useEffect(() => {
    fetchNotificationCount();
  }, []);

  const handleClearCache = async () => {
    // 1. Wipe backend memory cache (notifications, submissions ledger, snapshots)
    try {
      await fetch('/api/v1/clear-cache', {
        method: 'POST',
      });
    } catch (e) {
      console.error('Failed to clear backend cache:', e);
    }

    // 2. Reset frontend state to clean idle standby
    setDecision(null);
    setPipelineStatus({
      'intake-agent': 'idle',
      'risk-agent': 'idle',
      'pricing-agent': 'idle',
      'compliance-agent': 'idle',
      'orchestrator-agent': 'idle',
      'feedback-agent': 'idle',
    });
    setSelectedPresetId('');
    setRawText('');
    setNotificationsCount(0); // Wipe active notifications
    setCacheVersion((v) => v + 1); // Force child tabs to reload empty data
    setCurrentView('workspace');
  };

  const handleSelectPreset = (preset) => {
    setSelectedPresetId(preset.id);
    setRawText(preset.text);
  };

  const runPipelineAnimation = async () => {
    const agents = ['intake-agent', 'risk-agent', 'pricing-agent', 'compliance-agent', 'orchestrator-agent', 'feedback-agent'];

    for (let i = 0; i < agents.length; i++) {
      const agentId = agents[i];
      setPipelineStatus((prev) => ({
        ...prev,
        [agentId]: 'running',
      }));
      await new Promise((r) => setTimeout(r, 320)); // Sequential step delay
      setPipelineStatus((prev) => ({
        ...prev,
        [agentId]: 'completed',
      }));
    }
  };

  const handleUnderwriteSubmit = async () => {
    if (!rawText.trim()) return;

    setIsLoading(true);
    // Reset all nodes to idle before sequential run
    setPipelineStatus({
      'intake-agent': 'idle',
      'risk-agent': 'idle',
      'pricing-agent': 'idle',
      'compliance-agent': 'idle',
      'orchestrator-agent': 'idle',
      'feedback-agent': 'idle',
    });

    try {
      // Start sequential visualizer animation
      const animPromise = runPipelineAnimation();

      // Submit API request
      const response = await fetch('/api/v1/underwrite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          raw_text: rawText,
          submission_type: 'text',
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const result = await response.json();
      await animPromise; // Ensure full animation finishes
      setDecision(result);
      fetchNotificationCount();
      setCacheVersion((v) => v + 1);
    } catch (err) {
      console.error('Underwriting pipeline failed:', err);
      alert(`Error running underwriting pipeline: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOverrideDecision = async ({ submissionId, decisionType, comments }) => {
    try {
      const response = await fetch('/api/v1/override', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          submission_id: submissionId,
          decision_type: decisionType,
          comments: comments,
          underwriter_id: `${selectedRole} (Active Session)`,
        }),
      });

      if (response.ok) {
        const updated = await response.json();
        setDecision(updated);
        fetchNotificationCount();
        setCacheVersion((v) => v + 1);
      }
    } catch (e) {
      console.error('Failed to submit underwriter override:', e);
    }
  };

  const handleSelectHistoricalSubmission = (historicalDecision) => {
    setDecision(historicalDecision);
    if (historicalDecision.submission_data?.raw_text) {
      setRawText(historicalDecision.submission_data.raw_text);
    }
    setCurrentView('workspace');
    setActiveTab('risk');
  };

  const handleHydrateSession = (hydratedDecision) => {
    setDecision(hydratedDecision);
    setCurrentView('workspace');
    setActiveTab('review');
    fetchNotificationCount();
  };

  return (
    <div className="app-container">
      <Header
        selectedRole={selectedRole}
        onRoleChange={setSelectedRole}
        unreadNotificationsCount={notificationsCount}
        onOpenNotifications={() => setIsNotificationsOpen(true)}
        onToggleSidebar={() => setIsSidebarOpen(true)}
      />

      {/* Left Sliding Hamburger Drawer */}
      <SidebarDrawer
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentView={currentView}
        onSelectView={(view) => setCurrentView(view)}
        notificationsCount={notificationsCount}
        onOpenNotifications={() => setIsNotificationsOpen(true)}
        onClearCache={handleClearCache}
      />

      <main className="main-content">
        {/* ── 1. ACTIVE UNDERWRITING WORKSPACE VIEW ── */}
        {currentView === 'workspace' && (
          <>
            {/* Active RBAC Role Context Banner */}
            <RbacContextBanner selectedRole={selectedRole} />

            {/* Top 2-Column Split: Ingestion Studio (Left) & Pipeline / Banner (Right) */}
            <div className="split-grid">
              {/* Left Column: ACORD Application Input & Dropdown Scenario Selector */}
              <div>
                <SubmissionPanel
                  rawText={rawText}
                  onTextChange={setRawText}
                  onSubmit={handleUnderwriteSubmit}
                  isLoading={isLoading}
                  onSelectPreset={handleSelectPreset}
                  selectedPresetId={selectedPresetId}
                />
              </div>

              {/* Right Column: Live Pipeline Visualizer & Triage Banner */}
              <div>
                <div className="enterprise-card">
                  <div className="card-header">
                    <div className="card-header-left">
                      <span>🔄 Agent Pipeline Status & Live Execution Flow</span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <select
                        style={{
                          padding: '4px 10px',
                          fontSize: '0.75rem',
                          borderRadius: '6px',
                          border: '1px solid #cbd5e1',
                          background: '#f8fafc',
                          fontWeight: 600,
                          color: '#1e3a8a',
                          cursor: 'pointer',
                          outline: 'none'
                        }}
                        onChange={(e) => setInspectedAgentId(e.target.value)}
                        value=""
                      >
                        <option value="" disabled>🔍 Inspect Any Agent Logic...</option>
                        <option value="intake-agent">📥 Intake Agent</option>
                        <option value="risk-agent">🔍 Risk Profiling Agent</option>
                        <option value="pricing-agent">💰 Pricing Engine</option>
                        <option value="compliance-agent">⚖️ Compliance Agent</option>
                        <option value="orchestrator-agent">🎯 Orchestrator Agent</option>
                        <option value="feedback-agent">📊 Feedback & Learning Agent</option>
                        <option value="mcp-open-meteo-geocoding">📍 Open-Meteo Geocoding MCP</option>
                        <option value="mcp-fema-flood">🌊 FEMA Flood Zone MCP</option>
                        <option value="mcp-usgs-seismic">🌋 USGS Seismic MCP</option>
                        <option value="mcp-open-meteo-weather">🌪️ Open-Meteo Weather MCP</option>
                      </select>
                    </div>
                  </div>

                  <PipelineVisualizer
                    pipelineStatus={pipelineStatus}
                    onSelectAgent={(agentId) => setInspectedAgentId(agentId)}
                  />

                  {decision ? (
                    <>
                      <DecisionBanner decision={decision} />

                      {/* Prominent Action Card for Manual Review */}
                      <UnderwriterReviewActionCard
                        decision={decision}
                        onOverrideDecision={handleOverrideDecision}
                        selectedRole={selectedRole}
                      />
                    </>
                  ) : (
                    <div
                      style={{
                        padding: '24px',
                        textAlign: 'center',
                        background: '#f8fafc',
                        borderRadius: '10px',
                        border: '1px dashed #cbd5e1',
                        color: '#64748b',
                        fontSize: '0.85rem'
                      }}
                    >
                      <div>🏢 <b>System Idle & Standby:</b> Select an underwriting scenario from the dropdown and click <b>"🚀 Begin Underwriting Assessment"</b> to initiate the sequential multi-agent flow.</div>
                    </div>
                  )}
                </div>

                {/* Real-Time Location Intelligence & MCP Feeds Card */}
                {decision && decision.location_intelligence && (
                  <LocationIntelligenceCard locationIntelligence={decision.location_intelligence} />
                )}
              </div>
            </div>

            {/* Bottom Workspace: Tabbed Results for Active Scenario */}
            <div className="tabs-nav">
              <button
                type="button"
                className={`tab-nav-btn ${activeTab === 'risk' ? 'active' : ''}`}
                onClick={() => setActiveTab('risk')}
              >
                <Activity size={16} />
                <span>Risk Profile & Radar</span>
              </button>

              <button
                type="button"
                className={`tab-nav-btn ${activeTab === 'pricing' ? 'active' : ''}`}
                onClick={() => setActiveTab('pricing')}
              >
                <DollarSign size={16} />
                <span>Pricing & $10K Cap</span>
              </button>

              <button
                type="button"
                className={`tab-nav-btn ${activeTab === 'compliance' ? 'active' : ''}`}
                onClick={() => setActiveTab('compliance')}
              >
                <ShieldCheck size={16} />
                <span>Statutory Compliance (10 Rules)</span>
              </button>

              <button
                type="button"
                className={`tab-nav-btn ${activeTab === 'sandbox' ? 'active' : ''}`}
                onClick={() => setActiveTab('sandbox')}
              >
                <Sliders size={16} />
                <span>What-If Sandbox</span>
              </button>

              <button
                type="button"
                className={`tab-nav-btn ${activeTab === 'review' ? 'active' : ''}`}
                onClick={() => setActiveTab('review')}
              >
                <FileText size={16} />
                <span>Senior Underwriter Desk</span>
              </button>
            </div>

            {/* Tab Contents */}
            {activeTab === 'risk' && <TabRisk riskProfile={decision?.risk_profile} />}
            {activeTab === 'pricing' && <TabPricing pricing={decision?.pricing} />}
            {activeTab === 'compliance' && <TabCompliance compliance={decision?.compliance} />}
            {activeTab === 'sandbox' && <TabSandbox decision={decision} />}
            {activeTab === 'review' && (
              <TabReviewDesk
                decision={decision}
                onOverrideDecision={handleOverrideDecision}
                onHydrateSession={handleHydrateSession}
                selectedRole={selectedRole}
              />
            )}
          </>
        )}

        {/* ── ISOLATED VIEW: ENTERPRISE MEMORY BANK (ACCESSED VIA HAMBURGER MENU) ── */}
        {currentView === 'memory' && (
          <div>
            <div className="isolated-view-header">
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
                  🧠 Enterprise Memory Bank & Asynchronous Runtime
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  90-day cold-storage snapshot persistence, cross-week context retrieval, and zero-data-retention restoral
                </div>
              </div>
              <button
                type="button"
                className="back-to-workspace-btn"
                onClick={() => setCurrentView('workspace')}
              >
                <ArrowLeft size={16} />
                <span>Return to Active Workspace</span>
              </button>
            </div>

            <TabMemoryBank
              key={cacheVersion}
              onHydrateSession={handleHydrateSession}
            />
          </div>
        )}

        {/* ── 2. ISOLATED VIEW: PORTFOLIO ANALYTICS & HISTORY ── */}
        {currentView === 'analytics' && (
          <div>
            <div className="isolated-view-header">
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
                  📊 Portfolio Analytics & Submissions History
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Cross-fleet commercial portfolio intelligence, binding ratios, and historical records
                </div>
              </div>
              <button
                type="button"
                className="back-to-workspace-btn"
                onClick={() => setCurrentView('workspace')}
              >
                <ArrowLeft size={16} />
                <span>Return to Active Workspace</span>
              </button>
            </div>

            <TabPortfolioAnalytics
              key={cacheVersion}
              onSelectSubmission={handleSelectHistoricalSubmission}
            />
          </div>
        )}

        {/* ── 3. ISOLATED VIEW: AUDIT TRAIL & OTEL TELEMETRY ── */}
        {currentView === 'audit' && (
          <div>
            <div className="isolated-view-header">
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
                  🔍 OpenTelemetry Audit Trail & Telemetry
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Distributed span execution traces, latency metrics, and Model Armor zero-retention logs
                </div>
              </div>
              <button
                type="button"
                className="back-to-workspace-btn"
                onClick={() => setCurrentView('workspace')}
              >
                <ArrowLeft size={16} />
                <span>Return to Active Workspace</span>
              </button>
            </div>

            <TabAudit decision={decision} />
          </div>
        )}

        {/* ── 4. ISOLATED VIEW: AGENT REGISTRY & RBAC ── */}
        {currentView === 'registry' && (
          <div>
            <div className="isolated-view-header">
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', fontFamily: 'Outfit, sans-serif' }}>
                  📋 Enterprise Agent Registry & Access Control
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Catalog of 10 registered autonomous agents, versioning, health checks, and cross-department RBAC
                </div>
              </div>
              <button
                type="button"
                className="back-to-workspace-btn"
                onClick={() => setCurrentView('workspace')}
              >
                <ArrowLeft size={16} />
                <span>Return to Active Workspace</span>
              </button>
            </div>

            <TabRegistry />
          </div>
        )}
      </main>

      {/* Agent Deep-Dive Modal Inspector */}
      {inspectedAgentId && (
        <AgentInspector
          agentId={inspectedAgentId}
          decision={decision}
          onClose={() => setInspectedAgentId(null)}
        />
      )}

      {/* Underwriter Notifications Modal */}
      <NotificationsModal
        isOpen={isNotificationsOpen}
        onClose={() => {
          setIsNotificationsOpen(false);
          fetchNotificationCount();
        }}
      />
    </div>
  );
}

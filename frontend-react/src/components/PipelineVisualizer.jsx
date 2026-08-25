import React from 'react';
import { CheckCircle2, Loader2 } from 'lucide-react';

const AGENTS = [
  { id: 'intake-agent', name: 'Intake Agent', fullName: 'Intake Agent', icon: '📥' },
  { id: 'risk-agent', name: 'Risk Profiling', fullName: 'Risk Profiling Agent', icon: '🔍' },
  { id: 'pricing-agent', name: 'Pricing Engine', fullName: 'Pricing Engine Agent', icon: '💰' },
  { id: 'compliance-agent', name: 'Compliance', fullName: 'Compliance Agent', icon: '⚖️' },
  { id: 'orchestrator-agent', name: 'Orchestrator', fullName: 'Orchestrator Agent', icon: '🎯' },
  { id: 'feedback-agent', name: 'Feedback', fullName: 'Feedback & Learning Agent', icon: '📊' },
];

export default function PipelineVisualizer({ pipelineStatus, onSelectAgent }) {
  return (
    <div className="pipeline-track">
      {AGENTS.map((agent, index) => {
        const status = pipelineStatus[agent.id] || 'idle';
        return (
          <React.Fragment key={agent.id}>
            <div
              className={`pipeline-node ${status}`}
              onClick={() => onSelectAgent && onSelectAgent(agent.id)}
              style={{ cursor: 'pointer' }}
              title={`Click to inspect ${agent.fullName}`}
            >
              <div className="pipeline-icon-circle">
                {status === 'running' ? (
                  <Loader2 size={20} className="animate-spin" color="#1976d2" />
                ) : status === 'completed' ? (
                  <CheckCircle2 size={22} color="#16a34a" />
                ) : (
                  <span>{agent.icon}</span>
                )}
              </div>
              <div className="pipeline-name">{agent.name}</div>
              <div className={`pipeline-node-status ${status}`}>
                {status === 'running' ? 'in progress' : status}
              </div>
            </div>
            {index < AGENTS.length - 1 && (
              <div
                style={{
                  height: '2px',
                  flex: '0.4',
                  background: status === 'completed' ? '#86efac' : '#e2e8f0',
                  margin: '0 4px',
                  marginBottom: '26px'
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

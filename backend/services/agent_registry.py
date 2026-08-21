"""
Agent Registry Service

Central catalog for publishing, versioning, and discovering
enterprise-approved agents.  Supports lifecycle management
(registered → active → deprecated → retired).

In production this maps to Firestore; locally uses in-memory store.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from backend.models.schemas import AgentRegistryEntry, AgentStatus


class AgentRegistry:
    """Singleton registry for all platform agents."""

    _instance: Optional["AgentRegistry"] = None
    _agents: Dict[str, AgentRegistryEntry] = {}

    def __new__(cls) -> "AgentRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._agents = {}
        return cls._instance

    def register_agent(self, entry: AgentRegistryEntry) -> None:
        """Register or update an agent in the catalog."""
        self._agents[entry.agent_id] = entry

    def get_agent(self, agent_id: str) -> Optional[AgentRegistryEntry]:
        """Retrieve an agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[AgentRegistryEntry]:
        """List all registered agents."""
        return list(self._agents.values())

    def update_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update the status of an agent."""
        if agent_id in self._agents:
            self._agents[agent_id].status = status
            if status == AgentStatus.RUNNING:
                self._agents[agent_id].last_active = datetime.utcnow()

    def record_execution(self, agent_id: str, latency_ms: float, success: bool) -> None:
        """Record an execution event for metrics."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.total_executions += 1
            agent.last_active = datetime.utcnow()
            # Rolling average latency
            n = agent.total_executions
            agent.avg_latency_ms = round(
                ((agent.avg_latency_ms * (n - 1)) + latency_ms) / n, 2
            )
            # Success rate
            if not success:
                agent.success_rate = round(
                    ((agent.success_rate * (n - 1)) + 0) / n, 2
                )
                agent.health = "Degraded"
            else:
                agent.success_rate = round(
                    ((agent.success_rate * (n - 1)) + 100) / n, 2
                )
                agent.health = "Healthy" if agent.success_rate > 95 else "Degraded"

    def get_health_summary(self) -> Dict[str, str]:
        """Get health status of all agents."""
        return {a.agent_id: a.health for a in self._agents.values()}


def initialize_registry() -> AgentRegistry:
    """Pre-register all platform agents."""
    registry = AgentRegistry()

    agents = [
        AgentRegistryEntry(
            agent_id="intake-agent",
            agent_name="Intake Agent",
            version="1.0.0",
            description="Parses and structures broker submissions (text/PDF) into standardized data format.",
            capabilities=["Document Parsing", "Entity Extraction", "PDF Processing", "ACORD Form Recognition"],
            tools=["document_parser", "pdf_extractor"],
            department="Submission Processing",
            authorized_departments=["Underwriting", "Claims Triage", "Broker Services", "Policy Admin"],
            rbac_roles=["Underwriter", "Claims_Adjuster", "Broker_API_Client", "Operations"],
            sovereignty_region="Google Cloud us-central1 (Iowa - Primary)",
            api_endpoint="/api/v1/agents/intake/parse",
        ),
        AgentRegistryEntry(
            agent_id="risk-agent",
            agent_name="Risk Profiling Agent",
            version="1.0.0",
            description="Evaluates 6 risk dimensions and computes composite risk score with hazard zone detection.",
            capabilities=["Risk Scoring", "Hazard Detection", "Auto-Approve/Decline", "Risk Factor Analysis"],
            tools=["risk_calculator", "hazard_zone_lookup"],
            department="Risk Assessment",
            authorized_departments=["Underwriting", "Actuarial Science", "Loss Control", "Reinsurance Triage"],
            rbac_roles=["Underwriter", "Risk_Engineer", "Actuary", "Auditor"],
            sovereignty_region="Google Cloud us-central1 (Iowa - Primary)",
            api_endpoint="/api/v1/agents/risk/evaluate",
        ),
        AgentRegistryEntry(
            agent_id="pricing-agent",
            agent_name="Pricing & Product Agent",
            version="1.0.0",
            description="Calculates insurance premium using actuarial-style base-rate × modifier model (capped at $10K).",
            capabilities=["Premium Calculation", "Product Matching", "Rating Factor Analysis", "Cap Enforcement"],
            tools=["pricing_engine", "product_matcher"],
            department="Actuarial & Pricing",
            authorized_departments=["Underwriting", "Actuarial Science", "Product Management", "Finance"],
            rbac_roles=["Underwriter", "Actuary", "Pricing_Analyst", "Product_Owner"],
            sovereignty_region="Google Cloud us-central1 (Iowa - Primary)",
            api_endpoint="/api/v1/agents/pricing/calculate",
        ),
        AgentRegistryEntry(
            agent_id="compliance-agent",
            agent_name="Compliance Agent",
            version="1.0.0",
            description="Validates underwriting decisions against 10 regulatory, financial, and fairness rules.",
            capabilities=["Regulatory Compliance", "Fair Lending", "PII Protection", "Audit Trail"],
            tools=["compliance_checker", "pii_scanner"],
            department="Legal & Compliance",
            authorized_departments=["Legal", "Compliance", "Internal Audit", "Risk Governance"],
            rbac_roles=["Compliance_Officer", "Legal_Counsel", "Auditor", "Underwriter"],
            sovereignty_region="Google Cloud us-central1 (Iowa - Primary)",
            api_endpoint="/api/v1/agents/compliance/validate",
        ),
        AgentRegistryEntry(
            agent_id="orchestrator-agent",
            agent_name="Orchestrator Agent",
            version="1.0.0",
            description="Coordinates the sequential agent pipeline and makes final underwriting decision.",
            capabilities=["Pipeline Orchestration", "Decision Logic", "Human-in-Loop Routing", "Notification"],
            tools=["decision_engine", "notification_sender"],
            department="Underwriting Operations",
            authorized_departments=["Underwriting", "Executive Leadership", "Operations", "Broker Services"],
            rbac_roles=["Senior_Underwriter", "Operations_Manager", "CUO"],
            sovereignty_region="Google Cloud us-central1 (Iowa - Primary)",
            api_endpoint="/api/v1/agents/orchestrator/execute",
        ),
        AgentRegistryEntry(
            agent_id="feedback-agent",
            agent_name="Feedback & Learning Agent",
            version="1.0.0",
            description="Generates executive summaries, portfolio insights, and learning recommendations.",
            capabilities=["Summarization", "Trend Analysis", "Portfolio Analytics", "Improvement Suggestions"],
            tools=["summary_generator", "trend_analyzer"],
            department="Analytics & Strategy",
            authorized_departments=["Executive Board", "Portfolio Analytics", "Actuarial", "Underwriting"],
            rbac_roles=["Chief_Underwriting_Officer", "Portfolio_Manager", "Actuary"],
            sovereignty_region="Google Cloud us-central1 (Iowa - Primary)",
            api_endpoint="/api/v1/agents/feedback/synthesize",
        ),
        # ── MCP Data Fetcher Sub-Agents ─────────────────────────────
        AgentRegistryEntry(
            agent_id="mcp-open-meteo-geocoding",
            agent_name="Open-Meteo Geocoding MCP",
            version="1.0.0",
            description="Sub-agent connector providing address normalization, geographic coordinates (lat/long), and elevation.",
            capabilities=["Geocoding", "Address Normalization", "Spatial Verification", "Elevation Lookup"],
            tools=["open_meteo_geocoding_api", "geospatial_normalizer"],
            department="External Intelligence / MCP",
            authorized_departments=["Submission Processing", "Underwriting", "Operations"],
            rbac_roles=["Underwriter", "Operations", "Broker_API_Client"],
            sovereignty_region="Global Open-Meteo REST / Local Simulation",
            api_endpoint="https://geocoding-api.open-meteo.com/v1/search",
        ),
        AgentRegistryEntry(
            agent_id="mcp-fema-flood",
            agent_name="FEMA Flood Zone MCP",
            version="1.0.0",
            description="Sub-agent connector providing FEMA NFHL flood zone classification, SFHA status, and actuarial flood scoring.",
            capabilities=["Flood Zone Determination", "SFHA Assessment", "Base Flood Elevation", "Inundation Scoring"],
            tools=["fema_nfhl_gis", "open_fema_api"],
            department="External Intelligence / MCP",
            authorized_departments=["Risk Assessment", "Underwriting", "Actuarial Science"],
            rbac_roles=["Underwriter", "Risk_Engineer", "Actuary"],
            sovereignty_region="FEMA Open Data / Geospatial NFHL",
            api_endpoint="https://hazards.fema.gov/gis/nfhl/rest",
        ),
        AgentRegistryEntry(
            agent_id="mcp-usgs-seismic",
            agent_name="USGS Seismic MCP",
            version="1.0.0",
            description="Sub-agent connector providing USGS earthquake catalogs, fault line proximity, and Peak Ground Acceleration (PGA).",
            capabilities=["Earthquake Hazard Scoring", "Fault Proximity Analysis", "Historical Event Frequency", "PGA Calculation"],
            tools=["usgs_earthquake_api", "fault_line_database"],
            department="External Intelligence / MCP",
            authorized_departments=["Risk Assessment", "Underwriting", "Loss Control"],
            rbac_roles=["Underwriter", "Risk_Engineer", "Actuary"],
            sovereignty_region="USGS Earthquake Hazards Program",
            api_endpoint="https://earthquake.usgs.gov/fdsnws/event/1/query",
        ),
        AgentRegistryEntry(
            agent_id="mcp-open-meteo-weather",
            agent_name="Open-Meteo Weather MCP",
            version="1.0.0",
            description="Sub-agent connector evaluating extreme wind gusts, hurricane exposure tiers (Cat 1–5), and convective storm intensity.",
            capabilities=["Hurricane Exposure Rating", "Max Wind Gust Telemetry", "Convective Storm Assessment", "Extreme Weather Scoring"],
            tools=["open_meteo_forecast_api", "climate_extremes_engine"],
            department="External Intelligence / MCP",
            authorized_departments=["Risk Assessment", "Underwriting", "Actuarial Science"],
            rbac_roles=["Underwriter", "Risk_Engineer", "Actuary"],
            sovereignty_region="Open-Meteo High-Resolution Weather Model",
            api_endpoint="https://api.open-meteo.com/v1/forecast",
        ),
    ]

    for agent in agents:
        registry.register_agent(agent)

    return registry

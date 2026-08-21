"""
Data Models & Schemas

Pydantic models for every data structure flowing through the
multi-agent underwriting pipeline.  These schemas enforce type
safety at every agent hand-off.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ────────────────────────────────────────────────────────────────────
# Enums
# ────────────────────────────────────────────────────────────────────

class RiskTier(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DecisionType(str, Enum):
    AUTO_APPROVED = "Auto-Approved"
    UNDERWRITER_APPROVED = "Underwriter Approved"
    MANUAL_REVIEW = "Manual Review Required"
    AUTO_DECLINED = "Auto-Declined"
    UNDERWRITER_DECLINED = "Underwriter Declined"


class AgentStatus(str, Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    COMPLETED = "Completed"
    ERROR = "Error"
    SKIPPED = "Skipped"


class ComplianceStatus(str, Enum):
    PASS = "Pass"
    WARNING = "Warning"
    FAIL = "Fail"


class SubmissionType(str, Enum):
    TEXT = "text"
    PDF = "pdf"


# ────────────────────────────────────────────────────────────────────
# Submission Input
# ────────────────────────────────────────────────────────────────────

class SubmissionInput(BaseModel):
    """Raw submission from broker / applicant."""
    submission_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    submission_type: SubmissionType = SubmissionType.TEXT
    raw_text: str = ""
    file_name: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


# ────────────────────────────────────────────────────────────────────
# Parsed Submission Data  (output of Intake Agent)
# ────────────────────────────────────────────────────────────────────

class PropertyDetails(BaseModel):
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    property_value: float = 0.0
    building_age_years: int = 0
    construction_type: str = ""
    square_footage: int = 0
    num_floors: int = 1
    has_sprinkler_system: bool = False
    has_fire_alarm: bool = False
    has_security_system: bool = False
    roof_condition: str = "Good"
    last_renovation_year: Optional[int] = None


class BusinessInfo(BaseModel):
    business_name: str = ""
    business_type: str = ""
    industry_code: str = ""
    annual_revenue: float = 0.0
    employee_count: int = 0
    years_in_business: int = 0
    has_valid_license: bool = True
    previous_policy_cancelled: bool = False
    cancellation_reason: Optional[str] = None


class ClaimsHistory(BaseModel):
    total_claims_3yr: int = 0
    total_claims_5yr: int = 0
    largest_claim_amount: float = 0.0
    claim_details: List[Dict[str, Any]] = Field(default_factory=list)


class CoverageRequest(BaseModel):
    coverage_types: List[str] = Field(default_factory=list)
    desired_limit: float = 0.0
    deductible_preference: float = 1000.0
    effective_date: Optional[str] = None
    additional_insureds: int = 0


class SubmissionData(BaseModel):
    """Structured submission data (output of Intake Agent)."""
    submission_id: str = ""
    business_info: BusinessInfo = Field(default_factory=BusinessInfo)
    property_details: PropertyDetails = Field(default_factory=PropertyDetails)
    claims_history: ClaimsHistory = Field(default_factory=ClaimsHistory)
    coverage_request: CoverageRequest = Field(default_factory=CoverageRequest)
    raw_summary: str = ""
    extraction_confidence: float = 0.0
    intake_notes: List[str] = Field(default_factory=list)


# ────────────────────────────────────────────────────────────────────
# Risk Profile  (output of Risk Profiling Agent)
# ────────────────────────────────────────────────────────────────────

class RiskDimension(BaseModel):
    name: str
    score: float = 0.0  # 0-100
    weight: float = 0.0
    factors: List[str] = Field(default_factory=list)
    recommendation: str = ""


class RiskProfile(BaseModel):
    """Risk assessment output."""
    submission_id: str = ""
    composite_score: float = 0.0  # 0-100
    risk_tier: RiskTier = RiskTier.LOW
    dimensions: List[RiskDimension] = Field(default_factory=list)
    hazard_zones_detected: List[str] = Field(default_factory=list)
    is_hazard_zone: bool = False
    auto_decline_triggers: List[str] = Field(default_factory=list)
    risk_summary: str = ""
    risk_factors: List[str] = Field(default_factory=list)
    mitigating_factors: List[str] = Field(default_factory=list)


# ────────────────────────────────────────────────────────────────────
# Pricing Recommendation  (output of Pricing Agent)
# ────────────────────────────────────────────────────────────────────

class PricingModifier(BaseModel):
    name: str
    factor: float = 1.0
    reason: str = ""


class PricingRecommendation(BaseModel):
    """Premium calculation output."""
    submission_id: str = ""
    base_premium: float = 0.0
    modifiers: List[PricingModifier] = Field(default_factory=list)
    modifier_product: float = 1.0
    calculated_premium: float = 0.0
    final_premium: float = 0.0  # After cap enforcement
    premium_capped: bool = False
    product_recommendation: str = ""
    coverage_limit: float = 0.0
    deductible: float = 1000.0
    pricing_notes: List[str] = Field(default_factory=list)
    pricing_breakdown: Dict[str, float] = Field(default_factory=dict)


# ────────────────────────────────────────────────────────────────────
# Compliance Report  (output of Compliance Agent)
# ────────────────────────────────────────────────────────────────────

class ComplianceCheck(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    status: ComplianceStatus = ComplianceStatus.PASS
    details: str = ""
    remediation: Optional[str] = None


class ComplianceReport(BaseModel):
    """Regulatory compliance assessment."""
    submission_id: str = ""
    overall_status: ComplianceStatus = ComplianceStatus.PASS
    checks: List[ComplianceCheck] = Field(default_factory=list)
    passed_count: int = 0
    warning_count: int = 0
    failed_count: int = 0
    compliance_score: float = 100.0
    regulatory_notes: List[str] = Field(default_factory=list)
    requires_manual_review: bool = False
    review_reasons: List[str] = Field(default_factory=list)


# ────────────────────────────────────────────────────────────────────
# Final Underwriting Decision  (output of Orchestrator / Feedback)
# ────────────────────────────────────────────────────────────────────

class UnderwritingDecision(BaseModel):
    """Final aggregated underwriting decision."""
    model_config = ConfigDict(extra="allow")

    submission_id: str = ""
    decision: DecisionType = DecisionType.MANUAL_REVIEW
    confidence_score: float = 0.0
    decision_rationale: str = ""
    executive_summary: str = ""

    # Sub-agent results
    submission_data: Optional[SubmissionData] = None
    risk_profile: Optional[RiskProfile] = None
    pricing: Optional[PricingRecommendation] = None
    compliance: Optional[ComplianceReport] = None

    # Human-in-loop
    requires_human_review: bool = False
    review_priority: str = "Normal"
    reviewer_notifications: List[str] = Field(default_factory=list)
    human_review_reasons: List[str] = Field(default_factory=list)
    underwriter_override: Optional[str] = None
    underwriter_comments: Optional[str] = None
    underwriter_reviewed_at: Optional[datetime] = None
    underwriter_id: Optional[str] = None

    # Metadata
    processing_time_seconds: float = 0.0
    agents_executed: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    portfolio_insights: List[str] = Field(default_factory=list)


# ────────────────────────────────────────────────────────────────────
# Agent Registry & Observability Models
# ────────────────────────────────────────────────────────────────────

class AgentRegistryEntry(BaseModel):
    """Metadata for a registered agent."""
    agent_id: str
    agent_name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    department: str = "Underwriting"
    authorized_departments: List[str] = Field(default_factory=lambda: ["Underwriting", "Claims", "Actuarial", "Compliance", "Broker Portal"])
    rbac_roles: List[str] = Field(default_factory=lambda: ["Underwriter", "Actuary", "Claims_Adjuster", "Compliance_Officer"])
    sovereignty_region: str = "Google Cloud us-central1 (Iowa)"
    api_endpoint: str = "/api/v1/agents"
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    total_executions: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 100.0
    health: str = "Healthy"


class SessionSnapshot(BaseModel):
    """Multi-week asynchronous session snapshot for long-running workflows."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    submission_id: str = ""
    status: str = "ACTIVE"  # ACTIVE, PENDING_REVIEW, HYDRATED, ARCHIVED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_days: int = 90
    sovereignty_region: str = "us-central1"
    audit_span_count: int = 0
    decision: Optional[UnderwritingDecision] = None


class AuditLogEntry(BaseModel):
    """OpenTelemetry-compatible audit log entry."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_name: str = ""
    action: str = ""
    input_summary: str = ""
    output_summary: str = ""
    status: str = "OK"
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    token_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PipelineStatus(BaseModel):
    """Real-time status of the entire agent pipeline."""
    submission_id: str = ""
    current_agent: str = ""
    agents: Dict[str, AgentStatus] = Field(default_factory=dict)
    progress_percent: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    audit_trail: List[AuditLogEntry] = Field(default_factory=list)


class NotificationMessage(BaseModel):
    """Notification for human-in-the-loop review."""
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    submission_id: str = ""
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    title: str = ""
    message: str = ""
    action_required: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False

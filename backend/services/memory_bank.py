"""
Memory Bank Service

Persistent cross-session state store for the underwriting platform.
In production, maps to Google Cloud Firestore.
Locally, uses an in-memory dictionary for demo reliability.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.models.schemas import (
    DecisionType,
    NotificationMessage,
    SessionSnapshot,
    UnderwritingDecision,
)


class MemoryBank:
    """
    Persistent state management for underwriting sessions.

    Stores submission results, agent decisions, notifications,
    and multi-week asynchronous session snapshots. Enables cross-session
    context: an underwriter or broker can re-hydrate and resume review
    weeks later without data loss.
    """

    _instance: Optional["MemoryBank"] = None

    def __new__(cls) -> "MemoryBank":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._submissions: Dict[str, UnderwritingDecision] = {}
            cls._snapshots: Dict[str, SessionSnapshot] = {}
            cls._notifications: List[NotificationMessage] = []
            cls._session_context: Dict[str, Dict[str, Any]] = {}
        if not hasattr(cls._instance, "_snapshots"):
            cls._instance._snapshots = {}
        if not hasattr(cls._instance, "_submissions"):
            cls._instance._submissions = {}
        if not hasattr(cls._instance, "_notifications"):
            cls._instance._notifications = []
        if not hasattr(cls._instance, "_session_context"):
            cls._instance._session_context = {}
        return cls._instance

    # ── Multi-Week Asynchronous Session Lifecycles ────────────────

    def create_session_snapshot(self, decision: UnderwritingDecision) -> SessionSnapshot:
        """Create a persistent multi-week session snapshot for asynchronous workflows."""
        snapshot = SessionSnapshot(
            submission_id=decision.submission_id,
            status="PENDING_REVIEW" if decision.requires_human_review else "COMPLETED",
            sovereignty_region="us-central1",
            audit_span_count=len(decision.agents_executed),
            decision=decision,
        )
        self._snapshots[snapshot.session_id] = snapshot
        return snapshot

    def resume_session(self, session_id: str) -> Optional[SessionSnapshot]:
        """Re-hydrate a long-running underwriting session from cold storage."""
        snapshot = self._snapshots.get(session_id)
        if snapshot:
            snapshot.last_accessed_at = datetime.utcnow()
            snapshot.status = "HYDRATED"
        return snapshot

    def list_snapshots(self) -> List[SessionSnapshot]:
        """List all active and archived multi-week session snapshots."""
        return list(self._snapshots.values())

    def seed_demo_snapshot(self) -> SessionSnapshot:
        """Seed a historical 14-day-old asynchronous session snapshot for demonstration."""
        from datetime import timedelta
        from backend.models.schemas import (
            BusinessInfo,
            LocationIntelligenceReport,
            SubmissionData,
            PropertyDetails,
            RiskProfile,
            RiskTier,
            SubmissionType,
            GeocodingData,
            FEMAFloodData,
        )

        hist_submission = SubmissionData(
            submission_id="HBV-9421-FL",
            business_info=BusinessInfo(
                business_name="Harborview Logistics & Cold Storage LLC",
                business_type="Commercial Warehousing & Cold Storage",
                annual_revenue=3400000.0,
                employee_count=24,
                years_in_business=6,
                state="FL",
                city="Tampa",
                zip_code="33602",
                property_address="702 Channelside Drive",
            ),
            property_details=PropertyDetails(
                property_value=2800000.0,
                building_age_years=8,
                construction_type="Reinforced Concrete",
                has_sprinkler_system=True,
                has_fire_alarm=True,
                has_security_system=True,
            ),
            location_intelligence=LocationIntelligenceReport(
                submission_id="HBV-9421-FL",
                geocoding=GeocodingData(
                    latitude=27.9442,
                    longitude=-82.4498,
                    elevation_m=4.2,
                    city="Tampa",
                    state="FL",
                ),
                fema_flood=FEMAFloodData(
                    flood_zone="Zone AE",
                    is_sfha=True,
                    flood_risk_score=75.0,
                ),
                composite_location_score=54.2,
                hazard_alerts=["FEMA Flood Zone AE detected in Tampa Coastal Sector"],
            ),
        )

        hist_decision = UnderwritingDecision(
            submission_id="HBV-9421-FL",
            decision=DecisionType.MANUAL_REVIEW,
            confidence_score=91.0,
            requires_human_review=True,
            review_reasons=[
                "SFHA Flood Zone AE detected (Special Flood Hazard Area - Tampa Bay)",
                "Commercial cargo valuation exceeds $2.5M threshold",
            ],
            decision_rationale="Asynchronous survey hold: Site structural engineering survey pending completion.",
            executive_summary="Commercial cold storage facility in Tampa Channel District. Automated risk scoring complete (Tier: Moderate); awaiting on-site surveyor report.",
            created_at=datetime.utcnow() - timedelta(days=14),
            agents_executed=["Intake Agent", "Open-Meteo Geocoding MCP", "FEMA Flood Zone MCP", "Risk Profiling Agent", "Pricing Agent", "Compliance Agent"],
            submission_data=hist_submission,
            risk_profile=RiskProfile(
                composite_score=58.5,
                risk_tier=RiskTier.MEDIUM,
                is_hazard_zone=True,
                hazard_zones_detected=["FEMA Flood Zone AE", "Hurricane Exposure Tier 3"],
            ),
        )

        snapshot = SessionSnapshot(
            session_id="SNAP-WK2-9421",
            submission_id="HBV-9421-FL",
            status="PENDING_REVIEW",
            created_at=datetime.utcnow() - timedelta(days=14),
            last_accessed_at=datetime.utcnow() - timedelta(days=14),
            ttl_days=90,
            sovereignty_region="us-central1",
            audit_span_count=6,
            decision=hist_decision,
        )
        self._snapshots[snapshot.session_id] = snapshot
        self._submissions[hist_decision.submission_id] = hist_decision
        return snapshot

    # ── Submission Storage ────────────────────────────────────────

    def store_decision(self, decision: UnderwritingDecision) -> None:
        """Persist a completed underwriting decision and create a multi-week snapshot."""
        self._submissions[decision.submission_id] = decision
        self.create_session_snapshot(decision)

    def get_decision(self, submission_id: str) -> Optional[UnderwritingDecision]:
        """Retrieve a decision by submission ID."""
        return self._submissions.get(submission_id)

    def list_decisions(self) -> List[UnderwritingDecision]:
        """List all stored decisions (most recent first)."""
        return sorted(
            self._submissions.values(),
            key=lambda d: d.created_at,
            reverse=True,
        )

    def get_decisions_by_status(self, decision_type: str) -> List[UnderwritingDecision]:
        """Filter decisions by type (Auto-Approved, Manual Review, Auto-Declined)."""
        return [d for d in self._submissions.values() if d.decision.value == decision_type]

    # ── Notification System ───────────────────────────────────────

    def add_notification(self, notification: NotificationMessage) -> None:
        """Add a notification to the queue."""
        self._notifications.append(notification)

    def get_notifications(self, unacknowledged_only: bool = True) -> List[NotificationMessage]:
        """Retrieve notifications."""
        if unacknowledged_only:
            return [n for n in self._notifications if not n.acknowledged]
        return list(self._notifications)

    def acknowledge_notification(self, notification_id: str) -> bool:
        """Mark a notification as acknowledged."""
        for n in self._notifications:
            if n.notification_id == notification_id:
                n.acknowledged = True
                return True
        return False

    def get_pending_reviews(self) -> List[UnderwritingDecision]:
        """Get all submissions pending human review."""
        return [
            d for d in self._submissions.values()
            if d.requires_human_review and d.decision.value == "Manual Review Required"
        ]

    def resolve_review(
        self,
        submission_id: str,
        decision_type: str,
        comments: str,
        underwriter_id: str = "Senior Underwriter (UW-ID: #4092)"
    ) -> Optional[UnderwritingDecision]:
        """Apply a human underwriter decision (Approve / Decline) to a pending submission."""
        decision = self._submissions.get(submission_id)
        if decision:
            decision.underwriter_override = decision_type.upper()
            decision.underwriter_comments = comments
            decision.underwriter_reviewed_at = datetime.utcnow()
            decision.underwriter_id = underwriter_id
            decision.requires_human_review = False

            if decision_type.upper() == "APPROVED":
                decision.decision = DecisionType.UNDERWRITER_APPROVED
                decision.underwriter_override = "APPROVED"
            else:
                decision.decision = DecisionType.UNDERWRITER_DECLINED
                decision.underwriter_override = "DECLINED"

            # Acknowledge any matching notification
            for n in self._notifications:
                if submission_id in n.message or submission_id in n.title:
                    n.acknowledged = True

            # Update snapshot
            self.create_session_snapshot(decision)
        return decision

    # ── Session Context ───────────────────────────────────────────

    def store_context(self, session_id: str, key: str, value: Any) -> None:
        """Store arbitrary context for a session."""
        if session_id not in self._session_context:
            self._session_context[session_id] = {}
        self._session_context[session_id][key] = value

    def get_context(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieve context for a session."""
        return self._session_context.get(session_id, {}).get(key)

    # ── Analytics ─────────────────────────────────────────────────

    def get_portfolio_stats(self) -> Dict[str, Any]:
        """Compute portfolio-level statistics with Underwriter Approved / Declined tracking."""
        decisions = list(self._submissions.values())
        if not decisions:
            return {
                "total_submissions": 0,
                "auto_approved": 0,
                "underwriter_approved": 0,
                "manual_review": 0,
                "auto_declined": 0,
                "underwriter_declined": 0,
                "avg_premium": 0,
                "avg_risk_score": 0,
            }

        underwriter_approved = sum(1 for d in decisions if d.decision == DecisionType.UNDERWRITER_APPROVED or getattr(d, 'underwriter_override', None) == "APPROVED")
        underwriter_declined = sum(1 for d in decisions if d.decision == DecisionType.UNDERWRITER_DECLINED or getattr(d, 'underwriter_override', None) == "DECLINED")
        auto_approved = sum(1 for d in decisions if d.decision == DecisionType.AUTO_APPROVED and getattr(d, 'underwriter_override', None) != "APPROVED")
        manual_review = sum(1 for d in decisions if (d.decision == DecisionType.MANUAL_REVIEW or d.requires_human_review) and not getattr(d, 'underwriter_override', None))
        auto_declined = sum(1 for d in decisions if d.decision == DecisionType.AUTO_DECLINED and getattr(d, 'underwriter_override', None) != "DECLINED")

        premiums = [d.pricing.final_premium for d in decisions if d.pricing]
        risk_scores = [d.risk_profile.composite_score for d in decisions if d.risk_profile]

        return {
            "total_submissions": len(decisions),
            "auto_approved": auto_approved,
            "underwriter_approved": underwriter_approved,
            "manual_review": manual_review,
            "auto_declined": auto_declined,
            "underwriter_declined": underwriter_declined,
            "avg_premium": round(sum(premiums) / len(premiums), 2) if premiums else 0,
            "avg_risk_score": round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0,
        }

    def clear_all(self) -> None:
        """Clear all stored submissions, session snapshots, and notifications."""
        self._submissions.clear()
        self._snapshots.clear()
        self._notifications.clear()


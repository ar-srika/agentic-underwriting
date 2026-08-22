"""
Observability Service

OpenTelemetry-compliant tracing and audit logging for the
entire agent pipeline.  Captures reasoning chains, latency,
token usage, and decision rationale for every agent step.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

from backend.models.schemas import AuditLogEntry


class ObservabilityService:
    """
    Pipeline-wide telemetry and audit trail.

    Provides span-based tracing analogous to OpenTelemetry, capturing
    each agent's execution as a "span" within a submission "trace".
    """

    _instance: Optional["ObservabilityService"] = None
    _traces: Dict[str, List[AuditLogEntry]] = {}

    def __new__(cls) -> "ObservabilityService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._traces = {}
        return cls._instance

    def start_trace(self, trace_id: str) -> None:
        """Begin a new trace for a submission."""
        self._traces[trace_id] = []

    def add_span(self, trace_id: str, entry: AuditLogEntry) -> None:
        """Add a span (agent step) to a trace."""
        if trace_id not in self._traces:
            self._traces[trace_id] = []
        self._traces[trace_id].append(entry)

    def get_trace(self, trace_id: str) -> List[AuditLogEntry]:
        """Retrieve all spans for a trace."""
        return self._traces.get(trace_id, [])

    def get_all_traces(self) -> Dict[str, List[AuditLogEntry]]:
        """Retrieve all traces."""
        return dict(self._traces)

    def clear_all(self) -> None:
        """Clear all recorded telemetry traces."""
        self._traces.clear()


    @contextmanager
    def trace_agent(
        self,
        trace_id: str,
        agent_name: str,
        action: str = "execute",
    ) -> Generator[AuditLogEntry, None, None]:
        """
        Context manager that creates a timed span for an agent step.

        Usage:
            with observability.trace_agent(trace_id, "Risk Agent") as span:
                result = risk_agent.run(data)
                span.output_summary = f"Risk score: {result.composite_score}"
        """
        entry = AuditLogEntry(
            trace_id=trace_id,
            agent_name=agent_name,
            action=action,
            start_time=datetime.utcnow(),
        )
        start = time.time()
        try:
            yield entry
            entry.status = "OK"
        except Exception as e:
            entry.status = f"ERROR: {str(e)}"
            raise
        finally:
            end = time.time()
            entry.end_time = datetime.utcnow()
            entry.duration_ms = round((end - start) * 1000, 2)
            self.add_span(trace_id, entry)

    def get_pipeline_metrics(self, trace_id: str) -> Dict[str, Any]:
        """Compute aggregate metrics for a pipeline run."""
        spans = self.get_trace(trace_id)
        if not spans:
            return {}

        total_duration = sum(s.duration_ms for s in spans)
        total_tokens = sum(s.token_count for s in spans)
        agent_durations = {s.agent_name: s.duration_ms for s in spans}
        errors = [s for s in spans if "ERROR" in s.status]

        return {
            "total_duration_ms": round(total_duration, 2),
            "total_tokens": total_tokens,
            "agent_count": len(spans),
            "agent_durations": agent_durations,
            "error_count": len(errors),
            "errors": [{"agent": e.agent_name, "error": e.status} for e in errors],
        }

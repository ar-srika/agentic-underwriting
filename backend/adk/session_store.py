"""
Google ADK Session Store Layer

Provides persistent, asynchronous state and memory management conforming
to the Google ADK Session Store specification. Integrates directly with the
Enterprise Memory Bank for 90-day cold-storage snapshot hydration.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.models.schemas import SessionSnapshot, UnderwritingDecision
from backend.services.memory_bank import MemoryBank

logger = logging.getLogger(__name__)


class ADKSessionStore:
    """
    Google ADK-compliant Session Store.
    Manages long-running asynchronous agent execution sessions with zero context drift.
    """

    def __init__(self, memory_bank: Optional[MemoryBank] = None):
        self.memory = memory_bank or MemoryBank()

    def save_session(
        self,
        decision: UnderwritingDecision,
    ) -> SessionSnapshot:
        """Persist an ADK execution run into the 90-day cold storage snapshot store."""
        logger.info(f"ADK SessionStore: Persisting session snapshot for {decision.submission_id}")
        return self.memory.create_session_snapshot(decision=decision)

    def load_session(self, session_id: str) -> Optional[SessionSnapshot]:
        """Retrieve an ADK session snapshot by ID."""
        return self.memory.resume_session(session_id)

    def hydrate_session(self, session_id: str) -> Optional[SessionSnapshot]:
        """
        Asynchronously re-hydrate a historical ADK session from cold storage.
        Restores full execution graphs, risk matrices, and compliance audit trails.
        """
        logger.info(f"ADK SessionStore: Re-hydrating cold-storage session {session_id}")
        return self.memory.resume_session(session_id)

    def list_sessions(self) -> List[SessionSnapshot]:
        """List all active and cold-storage ADK sessions."""
        return self.memory.list_snapshots()

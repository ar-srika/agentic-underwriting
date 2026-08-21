"""
Base MCP Connector Module

Defines base classes and data containers for Model Context Protocol (MCP)
external connectors and sub-agent data fetchers.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MCPResponse(BaseModel, Generic[T]):
    """Standardized response container for all MCP connector calls."""
    connector_id: str
    success: bool = True
    data: Optional[T] = None
    is_simulated: bool = False
    latency_ms: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseMCPConnector(ABC):
    """
    Abstract base class for external MCP data fetchers and connectors.
    Provides standard timeout management, latency metrics, error isolation,
    and automatic fallback to deterministic simulation.
    """

    def __init__(self, connector_id: str, name: str, timeout_seconds: float = 4.0):
        self.connector_id = connector_id
        self.name = name
        self.timeout_seconds = timeout_seconds

    def execute(self, **kwargs: Any) -> MCPResponse:
        """
        Execute the connector call with telemetry and resilient fallback.
        """
        start_time = time.perf_counter()
        try:
            result_data, is_simulated = self._fetch_data(**kwargs)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return MCPResponse(
                connector_id=self.connector_id,
                success=True,
                data=result_data,
                is_simulated=is_simulated,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning(f"MCP Connector [{self.connector_id}] live fetch error: {e}. Falling back to simulation.")
            try:
                simulated_data = self._simulate_fallback(**kwargs)
                return MCPResponse(
                    connector_id=self.connector_id,
                    success=True,
                    data=simulated_data,
                    is_simulated=True,
                    latency_ms=latency_ms,
                    error_message=f"Live API error: {str(e)[:120]} (fallback used)",
                )
            except Exception as sim_err:
                logger.error(f"MCP Connector [{self.connector_id}] fallback failed: {sim_err}")
                return MCPResponse(
                    connector_id=self.connector_id,
                    success=False,
                    data=None,
                    is_simulated=True,
                    latency_ms=latency_ms,
                    error_message=str(sim_err),
                )

    @abstractmethod
    def _fetch_data(self, **kwargs: Any) -> tuple[Any, bool]:
        """Fetch live data from remote API or MCP service. Returns (data, is_simulated)."""
        pass

    @abstractmethod
    def _simulate_fallback(self, **kwargs: Any) -> Any:
        """Produce deterministic, high-fidelity offline simulation fallback."""
        pass

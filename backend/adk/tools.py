"""
Google ADK Tool-Binding Layer

Decorates functions as formal Google ADK Tools with JSON schema reflection,
parameter validation, and execution hooks. Binds external MCP connectors
(Open-Meteo, FEMA, USGS) and internal calculation engines into the ADK runtime.
"""

from __future__ import annotations

import functools
import inspect
import logging
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ADKTool:
    """
    Formal Google ADK Tool specification.
    """

    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: str = "general",
    ):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip()
        self.category = category
        self.signature = inspect.signature(func)
        self.total_invocations: int = 0
        self.avg_latency_ms: float = 0.0

    def __call__(self, *args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = self.func(*args, **kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            self.total_invocations += 1
            n = self.total_invocations
            self.avg_latency_ms = round(
                ((self.avg_latency_ms * (n - 1)) + latency_ms) / n, 2
            )
            return result
        except Exception as e:
            logger.error(f"ADK Tool [{self.name}] execution error: {e}")
            raise e

    def to_schema(self) -> Dict[str, Any]:
        """Convert tool signature to ADK/OpenAPI-compliant JSON Schema."""
        properties = {}
        required = []
        for param_name, param in self.signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            param_type = "string"
            if param.annotation in (int, float):
                param_type = "number"
            elif param.annotation is bool:
                param_type = "boolean"
            elif param.annotation in (dict, Dict):
                param_type = "object"
            elif param.annotation in (list, List):
                param_type = "array"

            properties[param_name] = {"type": param_type}
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


class ADKToolRegistry:
    """Singleton catalog of all registered Google ADK tools."""

    _instance: Optional["ADKToolRegistry"] = None
    _tools: Dict[str, ADKTool] = {}

    def __new__(cls) -> "ADKToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._tools = {}
        return cls._instance

    @classmethod
    def register(cls, tool: ADKTool) -> None:
        cls._tools[tool.name] = tool

    @classmethod
    def get_tool(cls, name: str) -> Optional[ADKTool]:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[ADKTool]:
        return list(cls._tools.values())

    @classmethod
    def to_declarations(cls) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in cls._tools.values()]


def adk_tool(name: Optional[str] = None, description: Optional[str] = None, category: str = "general"):
    """
    Decorator to wrap any Python function as a formal Google ADK Tool.
    """
    def decorator(func: Callable) -> ADKTool:
        tool = ADKTool(func, name=name, description=description, category=category)
        ADKToolRegistry.register(tool)
        return tool
    return decorator


# ==============================================================================
# Formal Google ADK Tool Bindings for Model Context Protocol (MCP) Connectors
# ==============================================================================

from backend.connectors.geocoding_connector import geocode_address
from backend.connectors.fema_flood_connector import fetch_fema_flood_data
from backend.connectors.usgs_seismic_connector import fetch_usgs_seismic_data
from backend.connectors.open_meteo_weather_connector import fetch_weather_exposure
from backend.connectors.location_intelligence import LocationIntelligenceAggregator
from backend.tools.risk_calculator import calculate_risk
from backend.tools.pricing_engine import calculate_premium
from backend.tools.document_parser import parse_submission_text
from backend.models.schemas import SubmissionData, RiskProfile


@adk_tool(name="adk_geocode_tool", description="Normalizes commercial property addresses to decimal coordinates via Open-Meteo", category="mcp_location")
def adk_geocode_tool(address: str, city: str, state: str, zip_code: str):
    return geocode_address(address=address, city=city, state=state, zip_code=zip_code)


@adk_tool(name="adk_fema_flood_tool", description="Retrieves FEMA National Flood Hazard Layer (NFHL) GIS data and SFHA status", category="mcp_location")
def adk_fema_flood_tool(latitude: float, longitude: float, state: str = "TX"):
    return fetch_fema_flood_data(latitude=latitude, longitude=longitude, state=state)


@adk_tool(name="adk_usgs_seismic_tool", description="Analyzes proximity to active earthquake fault lines and 10-year seismic PGA shake risk", category="mcp_location")
def adk_usgs_seismic_tool(latitude: float, longitude: float):
    return fetch_usgs_seismic_data(latitude=latitude, longitude=longitude)


@adk_tool(name="adk_weather_exposure_tool", description="Queries historical hurricane wind extremes and severe storm tiers via Open-Meteo", category="mcp_location")
def adk_weather_exposure_tool(latitude: float, longitude: float, state: str = "TX", zip_code: str = "73301"):
    return fetch_weather_exposure(latitude=latitude, longitude=longitude, state=state, zip_code=zip_code)


@adk_tool(name="adk_location_intelligence_mcp_tool", description="Executes complete multi-feed Model Context Protocol (MCP) location research", category="mcp_location")
def adk_location_intelligence_mcp_tool(submission_id: str, address: str, city: str, state: str, zip_code: str):
    aggregator = LocationIntelligenceAggregator()
    return aggregator.gather(submission_id=submission_id, address=address, city=city, state=state, zip_code=zip_code)


@adk_tool(name="adk_document_parser_tool", description="Extracts structured fields from raw ACORD or broker submission text", category="intake")
def adk_document_parser_tool(raw_text: str, submission_id: str = ""):
    return parse_submission_text(raw_text, submission_id=submission_id)


@adk_tool(name="adk_risk_calculator_tool", description="Calculates 6-axis actuarial risk profile enriched with live MCP environmental feeds", category="actuarial")
def adk_risk_calculator_tool(data: SubmissionData, location_intelligence: Any = None):
    return calculate_risk(data, location_intelligence=location_intelligence)


@adk_tool(name="adk_pricing_calculator_tool", description="Calculates final annual premium within statutory bounds ($500-$10,000 cap)", category="actuarial")
def adk_pricing_calculator_tool(data: SubmissionData, profile: RiskProfile):
    return calculate_premium(data, profile)

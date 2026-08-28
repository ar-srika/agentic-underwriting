"""
Google ADK Agent Definitions

Defines formal Google ADK Agent instances integrating the official Google GenAI SDK
with registered ADK tools for document parsing, MCP location intelligence,
actuarial calculation, and compliance governance.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from backend.config import settings
from backend.adk.tools import ADKTool, ADKToolRegistry

logger = logging.getLogger(__name__)


class ADKAgent:
    """
    Formal Google ADK Agent representation.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        system_instruction: str,
        model: str = "gemini-3.7-flash",
        tools: Optional[List[ADKTool]] = None,
        runner_fn: Optional[Callable] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.model = model
        self.tools = tools or []
        self.runner_fn = runner_fn
        self.total_runs: int = 0
        self.total_tokens_estimated: int = 0

    def run(self, context: Any) -> Any:
        """Execute agent reasoning using Google GenAI SDK and ADK tools."""
        self.total_runs += 1
        if self.runner_fn:
            return self.runner_fn(context)
        return None

    def call_gemini(self, prompt: str) -> str:
        """Invoke Google GenAI SDK under this agent's identity and instruction."""
        return settings.call_gemini(prompt, system_instruction=self.system_instruction)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "tools_count": len(self.tools),
            "tool_names": [t.name for t in self.tools],
            "total_runs": self.total_runs,
        }


# ==============================================================================
# Instantiate the 5 Core Google ADK Fleet Agents
# ==============================================================================

from backend.agents.intake_agent import run_intake_agent
from backend.agents.risk_agent import run_risk_agent
from backend.agents.pricing_agent import run_pricing_agent
from backend.agents.compliance_agent import run_compliance_agent
from backend.agents.feedback_agent import run_feedback_agent

adk_intake_agent = ADKAgent(
    agent_id="adk-intake-agent",
    name="ADK Intake & Gap Resolution Agent",
    role="Document Intake & Entity Extractor",
    system_instruction="You are an expert commercial insurance intake analyst. Parse messy broker submissions, resolve missing parameters, and provide inline source evidence.",
    model="gemini-3.7-flash",
    tools=[
        ADKToolRegistry.get_tool("adk_document_parser_tool")
    ],
    runner_fn=run_intake_agent,
)

adk_risk_agent = ADKAgent(
    agent_id="adk-risk-agent",
    name="ADK Risk Profiling & MCP Agent",
    role="6-Axis Actuarial Risk Assessor",
    system_instruction="You are a senior commercial insurance risk engineer. Synthesize physical property characteristics with real-time Model Context Protocol (MCP) hazard feeds.",
    model="gemini-3.7-pro",
    tools=[
        ADKToolRegistry.get_tool("adk_location_intelligence_mcp_tool"),
        ADKToolRegistry.get_tool("adk_risk_calculator_tool"),
    ],
    runner_fn=run_risk_agent,
)

adk_pricing_agent = ADKAgent(
    agent_id="adk-pricing-agent",
    name="ADK Pricing Engine Agent",
    role="Actuarial Rate & Endorsement Specialist",
    system_instruction="You are an actuarial pricing specialist. Apply statutory limits and generate transparent premium endorsement rationale.",
    model="gemini-3.5-flash",
    tools=[
        ADKToolRegistry.get_tool("adk_pricing_calculator_tool")
    ],
    runner_fn=None,  # Multi-parameter runner wrapped in supervisor
)

adk_compliance_agent = ADKAgent(
    agent_id="adk-compliance-agent",
    name="ADK Statutory Compliance Agent",
    role="Regulatory Governance Officer",
    system_instruction="You are an insurance regulatory compliance officer. Enforce NAIC licensing, FCRA fair lending, AML, and environmental disclosures.",
    model="gemini-3.5-pro",
    tools=[],
    runner_fn=None,
)

adk_feedback_agent = ADKAgent(
    agent_id="adk-feedback-agent",
    name="ADK Feedback & CUO Synthesis Agent",
    role="Chief Underwriting Officer Executive Synthesizer",
    system_instruction="You are the Chief Underwriting Officer. Consolidate multi-agent findings into an executive underwriting summary for the board.",
    model="gemini-3.7-flash",
    tools=[],
    runner_fn=None,
)

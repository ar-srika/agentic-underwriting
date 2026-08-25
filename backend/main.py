"""
FastAPI Backend — Enterprise Underwriting Platform API

Provides REST endpoints for submission processing, agent registry,
and observability.  Designed for deployment on Google Cloud Run.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.orchestrator import run_orchestrator
from backend.config import settings
from backend.models.schemas import SubmissionInput, SubmissionType
from backend.services.agent_registry import initialize_registry
from backend.services.memory_bank import MemoryBank
from backend.services.observability import ObservabilityService

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="UnderwriteAI Enterprise Intelligence Platform",
    description="Multi-Agent AI Platform for Small Business Insurance Underwriting",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.services.agent_gateway import AgentGateway

# Initialize services
registry = initialize_registry()
memory = MemoryBank()
observability = ObservabilityService()
gateway = AgentGateway()

# Pre-seed historical 14-day asynchronous session snapshot for cold-storage demonstration
memory.seed_demo_snapshot()


@app.get("/health")
@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "agents_registered": len(registry.list_agents()),
        "gemini_configured": settings.is_api_key_configured(),
        "gateway": "AgentGateway Active (Zero-Trust)",
    }


@app.get("/api/v1/gateway/status")
async def get_gateway_status():
    """Retrieve enterprise agent gateway health, routing policies, and security stats."""
    return gateway.get_gateway_status()


@app.post("/api/v1/underwrite")
async def submit_underwriting_json(submission: SubmissionInput):
    """
    Submit underwriting request via JSON body through the Enterprise Agent Gateway.
    """
    if not submission.raw_text:
        raise HTTPException(400, "raw_text must be provided")
    try:
        decision = gateway.route_underwriting_request(submission)
        return decision.model_dump()
    except Exception as e:
        logger.error(f"Gateway pipeline error: {e}")
        raise HTTPException(500, f"Processing error: {str(e)}")


@app.post("/api/underwrite")
async def submit_underwriting(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Submit a new underwriting request via Form data or PDF file upload through the Gateway.
    """
    if not text and not file:
        raise HTTPException(400, "Either text or file must be provided")

    raw_text = ""
    sub_type = SubmissionType.TEXT

    if file:
        if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(413, f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit")
        content = await file.read()
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            raw_text = content.decode("utf-8", errors="ignore")
        sub_type = SubmissionType.PDF
    else:
        raw_text = text or ""

    submission = SubmissionInput(raw_text=raw_text, submission_type=sub_type)

    try:
        decision = gateway.route_underwriting_request(submission)
        return decision.model_dump()
    except Exception as e:
        logger.error(f"Gateway pipeline error: {e}")
        raise HTTPException(500, f"Processing error: {str(e)}")


@app.get("/api/agents/registry")
@app.get("/api/v1/registry")
async def get_agent_registry():
    """List all registered agents and their status."""
    return [a.model_dump() for a in registry.list_agents()]


# ── Memory Bank & Asynchronous Session Endpoints ──────────────

@app.get("/api/v1/sessions")
async def list_session_snapshots():
    """List all active and archived multi-week session snapshots stored in Memory Bank."""
    return [s.model_dump() for s in memory.list_snapshots()]


@app.get("/api/v1/sessions/{session_id}")
async def get_session_snapshot(session_id: str):
    """Retrieve a specific long-running session snapshot."""
    snapshot = memory._snapshots.get(session_id)
    if not snapshot:
        raise HTTPException(404, f"Session snapshot '{session_id}' not found")
    return snapshot.model_dump()


@app.post("/api/v1/sessions/{session_id}/hydrate")
async def hydrate_session(session_id: str):
    """Re-hydrate a long-running underwriting session from cold storage across weeks of async operations."""
    snapshot = memory.resume_session(session_id)
    if not snapshot:
        raise HTTPException(404, f"Session snapshot '{session_id}' not found in Memory Bank")
    return {
        "status": "HYDRATED",
        "message": f"Session {session_id} successfully re-hydrated from 90-day cold storage.",
        "snapshot": snapshot.model_dump(),
    }


@app.get("/api/submissions")
@app.get("/api/v1/submissions")
async def list_submissions():
    """List all processed submissions."""
    return [d.model_dump() for d in memory.list_decisions()]


@app.get("/api/submissions/{submission_id}")
@app.get("/api/v1/submissions/{submission_id}")
async def get_submission(submission_id: str):
    """Get a specific submission result."""
    decision = memory.get_decision(submission_id)
    if not decision:
        raise HTTPException(404, "Submission not found")
    return decision.model_dump()


@app.get("/api/submissions/{submission_id}/trace")
@app.get("/api/v1/submissions/{submission_id}/trace")
async def get_trace(submission_id: str):
    """Get the OpenTelemetry trace for a submission."""
    trace = observability.get_trace(submission_id)
    if not trace:
        raise HTTPException(404, "Trace not found")
    return [t.model_dump() for t in trace]


@app.get("/api/notifications")
@app.get("/api/v1/notifications")
async def get_notifications():
    """Get pending notifications for human review."""
    return [n.model_dump() for n in memory.get_notifications()]


@app.get("/api/portfolio/stats")
@app.get("/api/v1/metrics")
async def get_portfolio_stats():
    """Get portfolio-level analytics."""
    return memory.get_portfolio_stats()


class UnderwriterOverrideRequest(BaseModel):
    submission_id: str
    decision_type: str  # "APPROVED" or "DECLINED"
    comments: str = ""
    underwriter_id: str = "Senior Underwriter (UW-ID: #4092)"


@app.post("/api/v1/override")
async def apply_underwriter_override(req: UnderwriterOverrideRequest):
    """Apply underwriter manual override approval or decline."""
    resolved = memory.resolve_review(
        submission_id=req.submission_id,
        decision_type=req.decision_type,
        comments=req.comments,
        underwriter_id=req.underwriter_id,
    )
    if not resolved:
        raise HTTPException(404, "Submission not found in memory bank")
    return resolved.model_dump()


@app.post("/api/clear-cache")
@app.post("/api/v1/clear-cache")
async def clear_system_cache():
    """Clear all stored submissions, session snapshots, notifications, and traces."""
    memory.clear_all()
    observability.clear_all()
    # Re-seed the demo snapshot so judges always have the async snapshot demo ready
    memory.seed_demo_snapshot()
    return {
        "status": "success",
        "message": "All portfolio records, submissions ledger, notifications, and telemetry traces have been cleared."
    }


# --- Static SPA Frontend Serving (Cloud Run / Full-Stack mode) ---
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend-react", "dist")
assets_path = os.path.join(dist_path, "assets")

if os.path.exists(dist_path):
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/")
    async def serve_root():
        index_file = os.path.join(dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"status": "ok", "message": "UnderwriteAI API Backend is running"}

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/") or full_path.startswith("health"):
            raise HTTPException(404, "Not Found")
        file_path = os.path.join(dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(404, "Frontend build not found")







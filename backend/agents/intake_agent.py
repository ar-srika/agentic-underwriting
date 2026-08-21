"""
Intake Agent

Parses raw broker submissions (text or PDF) into structured data.
Uses the document_parser tool for field extraction and optionally
calls Gemini for enhanced understanding of ambiguous content.
"""

from __future__ import annotations

import logging
from typing import Optional

from backend.config import settings
from backend.models.schemas import SubmissionData, SubmissionInput
from backend.tools.document_parser import parse_submission_text

logger = logging.getLogger(__name__)


def _enhance_with_gemini(raw_text: str, parsed: SubmissionData) -> SubmissionData:
    """
    Use Gemini 3.5 to fill in gaps left by the regex parser.

    This is the AI-enhanced step: Gemini reasons about the
    unstructured text to extract fields the regex missed.
    """
    if not settings.is_api_key_configured():
        parsed.intake_notes.append("ℹ Gemini enhancement skipped — API key not configured")
        return parsed

    try:
        prompt = f"""You are an expert insurance intake analyst. Analyze this broker submission and extract any missing fields.

Current extracted data:
- Business Name: {parsed.business_info.business_name or 'MISSING'}
- Business Type: {parsed.business_info.business_type or 'MISSING'}
- Annual Revenue: ${parsed.business_info.annual_revenue:,.0f}
- Employees: {parsed.business_info.employee_count}
- Property Address: {parsed.property_details.address or 'MISSING'}
- City: {parsed.property_details.city or 'MISSING'}
- State: {parsed.property_details.state or 'MISSING'}
- Property Value: ${parsed.property_details.property_value:,.0f}
- Building Age: {parsed.property_details.building_age_years} years
- Construction Type: {parsed.property_details.construction_type or 'MISSING'}
- Claims in 3yr: {parsed.claims_history.total_claims_3yr}
- Years in Business: {parsed.business_info.years_in_business}

Raw submission text:
{raw_text[:3000]}

For any fields marked MISSING, extract the value from the text if available.
Respond ONLY in this exact format (one field per line, only include fields you found):
BUSINESS_NAME: <value>
BUSINESS_TYPE: <value>
CITY: <value>
STATE: <value>
CONSTRUCTION_TYPE: <value>
ADDRESS: <value>

If a field is not in the text, do not include it."""

        result_text = settings.call_gemini(prompt).strip()

        # Parse Gemini's response and fill gaps
        for line in result_text.split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().upper()
            value = value.strip()

            if not value or value.upper() == "MISSING":
                continue

            if key == "BUSINESS_NAME" and not parsed.business_info.business_name:
                parsed.business_info.business_name = value
            elif key == "BUSINESS_TYPE" and not parsed.business_info.business_type:
                parsed.business_info.business_type = value
            elif key == "CITY" and not parsed.property_details.city:
                parsed.property_details.city = value
            elif key == "STATE" and not parsed.property_details.state:
                parsed.property_details.state = value
            elif key == "CONSTRUCTION_TYPE" and not parsed.property_details.construction_type:
                parsed.property_details.construction_type = value
            elif key == "ADDRESS" and not parsed.property_details.address:
                parsed.property_details.address = value

        parsed.intake_notes.append("✅ Gemini enhancement applied — missing fields filled")

    except Exception as e:
        logger.warning(f"Gemini enhancement failed: {e}")
        parsed.intake_notes.append(f"⚠ Gemini enhancement unavailable: {str(e)[:100]}")

    return parsed


def run_intake_agent(submission: SubmissionInput) -> SubmissionData:
    """
    Execute the Intake Agent pipeline.

    Steps:
    1. Parse raw text using document_parser tool (regex extraction)
    2. Enhance with Gemini 3.5 for ambiguous fields
    3. Apply defaults for critical missing fields

    Args:
        submission: Raw submission input (text or PDF-extracted text).

    Returns:
        SubmissionData with all extractable fields populated.
    """
    logger.info(f"Intake Agent processing submission {submission.submission_id}")

    # Step 1: Regex-based extraction (tool call)
    parsed = parse_submission_text(submission.raw_text, submission.submission_id)

    # Step 2: AI enhancement with Gemini
    parsed = _enhance_with_gemini(submission.raw_text, parsed)

    # Step 3: Apply sensible defaults
    if not parsed.business_info.business_type:
        parsed.business_info.business_type = "Small Business"
        parsed.intake_notes.append("ℹ Business type defaulted to 'Small Business'")

    if parsed.property_details.property_value <= 0:
        parsed.property_details.property_value = 300_000  # reasonable default
        parsed.intake_notes.append("ℹ Property value estimated at $300,000 (default)")

    if parsed.business_info.annual_revenue <= 0:
        parsed.business_info.annual_revenue = 500_000
        parsed.intake_notes.append("ℹ Annual revenue estimated at $500,000 (default)")

    if parsed.business_info.years_in_business <= 0:
        parsed.business_info.years_in_business = 3
        parsed.intake_notes.append("ℹ Years in business defaulted to 3")

    # Recalculate confidence after enhancement
    filled = sum([
        bool(parsed.business_info.business_name),
        bool(parsed.business_info.business_type),
        parsed.business_info.annual_revenue > 0,
        parsed.business_info.employee_count > 0,
        bool(parsed.property_details.address or parsed.property_details.city),
        parsed.property_details.property_value > 0,
        bool(parsed.property_details.construction_type),
        parsed.claims_history.total_claims_3yr >= 0,
    ])
    parsed.extraction_confidence = min(round(filled / 8 * 100, 1), 100.0)

    logger.info(f"Intake Agent completed — confidence: {parsed.extraction_confidence}%")
    return parsed

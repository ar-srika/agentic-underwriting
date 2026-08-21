"""
Document Parser Tool

Extracts structured data from raw text submissions and PDF files.
Uses pattern matching and heuristics to identify key underwriting
fields from free-form broker submission text.
"""

import re
from typing import Any, Dict, Optional

from backend.models.schemas import (
    BusinessInfo,
    ClaimsHistory,
    CoverageRequest,
    PropertyDetails,
    SubmissionData,
)


def _extract_currency(text: str, patterns: list[str]) -> float:
    """Extract a dollar amount near given keywords."""
    for pattern in patterns:
        match = re.search(
            rf"(?i){pattern}\s*[:=]?\s*\$?([\d,]+(?:\.\d{{2}})?)", text
        )
        if match:
            return float(match.group(1).replace(",", ""))
    return 0.0


def _extract_int(text: str, patterns: list[str]) -> int:
    """Extract an integer near given keywords."""
    for pattern in patterns:
        match = re.search(rf"(?i){pattern}\s*[:=]?\s*(\d+)", text)
        if match:
            return int(match.group(1))
    return 0


def _extract_field(text: str, patterns: list[str]) -> str:
    """Extract a text value near given keywords."""
    for pattern in patterns:
        match = re.search(rf"(?i){pattern}\s*[:=]?\s*(.+?)(?:\n|$)", text)
        if match:
            return match.group(1).strip().strip(".,;")
    return ""


def _detect_boolean(text: str, keywords: list[str]) -> bool:
    """Check if any keyword appears with an affirmative response."""
    for kw in keywords:
        pat = rf"(?i){kw}(?:\s*system)?\s*[:=]?\s*(yes|true|installed|active|present)"
        if re.search(pat, text):
            return True
    return False


def parse_submission_text(raw_text: str, submission_id: str = "") -> SubmissionData:
    """
    Parse raw broker submission text into structured SubmissionData.

    This is the primary tool called by the Intake Agent.  It uses
    regex-based extraction for known field patterns and returns a
    structured data object for downstream agents.

    Args:
        raw_text: Free-form text from broker email / ACORD form / pasted content.
        submission_id: Unique identifier for this submission.

    Returns:
        SubmissionData with all extractable fields populated.
    """
    text = raw_text.strip()

    # ── Business Information ──────────────────────────────────────
    business_info = BusinessInfo(
        business_name=_extract_field(text, [
            r"business\s*name", r"company\s*name", r"insured\s*name",
            r"applicant\s*name", r"dba", r"legal\s*name"
        ]),
        business_type=_extract_field(text, [
            r"business\s*type", r"type\s*of\s*business", r"industry",
            r"business\s*category", r"nature\s*of\s*business"
        ]),
        industry_code=_extract_field(text, [
            r"naics", r"sic\s*code", r"industry\s*code", r"class\s*code"
        ]),
        annual_revenue=_extract_currency(text, [
            r"annual\s*revenue", r"gross\s*revenue", r"annual\s*sales",
            r"revenue", r"gross\s*income"
        ]),
        employee_count=_extract_int(text, [
            r"employee\s*count", r"number\s*of\s*employees",
            r"employees", r"staff\s*count", r"headcount",r"total\s*employees"
        ]),
        years_in_business=_extract_int(text, [
            r"years\s*in\s*business", r"established",
            r"operating\s*since", r"years\s*of\s*operation"
        ]),
        has_valid_license=not bool(
            re.search(r"(?i)(no\s*valid\s*license|valid\s*license\s*:\s*no|license\s*expired|unlicensed|license\s*revoked)", text)
        ),
        previous_policy_cancelled=bool(
            re.search(r"(?i)(previous\s*policy\s*cancell\w*\s*:\s*yes|policy\s*cancell\w*|non-?renew)", text)
        ),
        cancellation_reason=_extract_field(text, [
            r"cancellation\s*reason", r"reason\s*for\s*cancellation",
            r"cancelled\s*for", r"cancell\w*\s*reason"
        ]),
    )

    # ── Property Details ──────────────────────────────────────────
    property_details = PropertyDetails(
        address=_extract_field(text, [
            r"property\s*address", r"location\s*address",
            r"street\s*address", r"address"
        ]),
        city=_extract_field(text, [r"city"]),
        state=_extract_field(text, [r"state"]),
        zip_code=_extract_field(text, [r"zip\s*code", r"zip", r"postal\s*code"]),
        property_value=_extract_currency(text, [
            r"property\s*value", r"building\s*value",
            r"replacement\s*value", r"total\s*insured\s*value", r"tiv"
        ]),
        building_age_years=_extract_int(text, [
            r"building\s*age", r"year\s*built", r"age\s*of\s*building",
            r"construction\s*year"
        ]),
        construction_type=_extract_field(text, [
            r"construction\s*type", r"building\s*construction",
            r"structure\s*type"
        ]),
        square_footage=_extract_int(text, [
            r"square\s*footage", r"sq\s*ft", r"square\s*feet", r"area"
        ]),
        num_floors=_extract_int(text, [
            r"floors", r"stories", r"number\s*of\s*floors"
        ]) or 1,
        has_sprinkler_system=_detect_boolean(text, [
            r"sprinkler", r"fire\s*suppression"
        ]),
        has_fire_alarm=_detect_boolean(text, [
            r"fire\s*alarm", r"smoke\s*detector", r"fire\s*detection"
        ]),
        has_security_system=_detect_boolean(text, [
            r"security\s*system", r"burglar\s*alarm", r"surveillance",
            r"cctv", r"monitored"
        ]),
        roof_condition=_extract_field(text, [
            r"roof\s*condition", r"roof\s*status"
        ]) or "Good",
    )

    # If city/state/zip were not on separate lines, try to parse from address line
    if property_details.address:
        addr_match = re.search(r",\s*([A-Za-z\s]+?),\s*([A-Za-z]{2})\s*(\d{5})?", property_details.address)
        if addr_match:
            if not property_details.city:
                property_details.city = addr_match.group(1).strip()
            if not property_details.state:
                property_details.state = addr_match.group(2).strip().upper()
            if not property_details.zip_code and addr_match.group(3):
                property_details.zip_code = addr_match.group(3).strip()
            # Clean up street address to remove the city/state/zip part
            property_details.address = property_details.address[:addr_match.start()].strip()
        else:
            # Check for State abbreviation anywhere in text if still missing
            if not property_details.state:
                st_match = re.search(r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b", text)
                if st_match:
                    property_details.state = st_match.group(1)
            if not property_details.zip_code:
                zip_match = re.search(r"\b(\d{5}(?:-\d{4})?)\b", text)
                if zip_match:
                    property_details.zip_code = zip_match.group(1)

    # ── Claims History ────────────────────────────────────────────
    claims_3yr = _extract_int(text, [
        r"claims?\s*(?:in\s*)?(?:the\s*)?(?:past\s*)?3\s*years?",
        r"3[- ]year\s*claims?", r"claims?\s*history",
        r"total\s*claims?\s*(?:3yr)?"
    ])
    claims_5yr = _extract_int(text, [
        r"claims?\s*(?:in\s*)?(?:the\s*)?(?:past\s*)?5\s*years?",
        r"5[- ]year\s*claims?"
    ]) or claims_3yr

    claims_history = ClaimsHistory(
        total_claims_3yr=claims_3yr,
        total_claims_5yr=claims_5yr,
        largest_claim_amount=_extract_currency(text, [
            r"largest\s*claim", r"biggest\s*claim", r"max\s*claim"
        ]),
    )

    # ── Coverage Request ──────────────────────────────────────────
    coverage_types = []
    coverage_keywords = {
        "General Liability": r"(?i)general\s*liability",
        "Property": r"(?i)property\s*(coverage|insurance)",
        "Business Interruption": r"(?i)business\s*interruption",
        "Workers Compensation": r"(?i)workers?\s*comp",
        "Professional Liability": r"(?i)professional\s*liability|e&o",
        "Commercial Auto": r"(?i)commercial\s*auto",
        "Cyber Liability": r"(?i)cyber\s*(liability|insurance)",
        "Umbrella": r"(?i)umbrella\s*(coverage|policy)",
    }
    for cov_name, cov_pattern in coverage_keywords.items():
        if re.search(cov_pattern, text):
            coverage_types.append(cov_name)
    if not coverage_types:
        coverage_types = ["General Liability", "Property"]

    coverage_request = CoverageRequest(
        coverage_types=coverage_types,
        desired_limit=_extract_currency(text, [
            r"coverage\s*limit", r"policy\s*limit", r"limit"
        ]) or 1_000_000.0,
        deductible_preference=_extract_currency(text, [
            r"deductible"
        ]) or 1000.0,
        effective_date=_extract_field(text, [
            r"effective\s*date", r"start\s*date", r"inception"
        ]),
    )

    # ── Extraction Confidence ─────────────────────────────────────
    filled_fields = sum([
        bool(business_info.business_name),
        bool(business_info.business_type),
        business_info.annual_revenue > 0,
        business_info.employee_count > 0,
        bool(property_details.address),
        property_details.property_value > 0,
        bool(property_details.construction_type),
        claims_history.total_claims_3yr >= 0,
    ])
    confidence = min(round(filled_fields / 8 * 100, 1), 100.0)

    notes = []
    if not business_info.business_name:
        notes.append("⚠ Business name could not be extracted")
    if property_details.property_value == 0:
        notes.append("⚠ Property value not found — using default estimates")
    if business_info.annual_revenue == 0:
        notes.append("⚠ Annual revenue not specified")

    return SubmissionData(
        submission_id=submission_id,
        business_info=business_info,
        property_details=property_details,
        claims_history=claims_history,
        coverage_request=coverage_request,
        raw_summary=text[:500],
        extraction_confidence=confidence,
        intake_notes=notes,
    )


def parse_pdf_text(pdf_text: str, submission_id: str = "") -> SubmissionData:
    """
    Parse text extracted from a PDF file.
    Delegates to parse_submission_text after basic cleanup.
    """
    # Clean up common PDF extraction artifacts
    cleaned = re.sub(r"\x0c", "\n", pdf_text)  # form-feed chars
    cleaned = re.sub(r" {3,}", "  ", cleaned)    # excessive spaces
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned) # excessive newlines
    return parse_submission_text(cleaned, submission_id)

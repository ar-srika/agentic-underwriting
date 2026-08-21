"""
Application Configuration Module

Centralizes all configuration, environment variables, and constants
for the Enterprise Underwriting Platform.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application-wide settings loaded from environment variables."""

    # --- Google AI ---
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-pro")

    # --- Application ---
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_NAME: str = "UnderwriteAI"
    APP_VERSION: str = "1.0.0"

    # --- Security ---
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_FILE_TYPES: list = os.getenv("ALLOWED_FILE_TYPES", "pdf,txt,docx").split(",")

    # --- Pricing Constraints ---
    MAX_PREMIUM: float = float(os.getenv("MAX_PREMIUM", "10000"))
    MIN_PREMIUM: float = float(os.getenv("MIN_PREMIUM", "500"))

    # --- Risk Decision Thresholds ---
    AUTO_APPROVE_THRESHOLD: int = int(os.getenv("AUTO_APPROVE_THRESHOLD", "35"))
    MANUAL_REVIEW_THRESHOLD: int = int(os.getenv("MANUAL_REVIEW_THRESHOLD", "65"))
    AUTO_DECLINE_THRESHOLD: int = int(os.getenv("AUTO_DECLINE_THRESHOLD", "80"))

    # --- Business Rules ---
    MAX_CLAIMS_FOR_APPROVAL: int = 2
    MAX_CLAIMS_BEFORE_DECLINE: int = 5
    HAZARD_ZONES = [
        "FEMA Flood Zone A", "FEMA Flood Zone V", "FEMA Flood Zone AE",
        "FEMA Flood Zone VE", "Seismic Zone 3", "Seismic Zone 4",
        "Wildfire WUI High", "Wildfire WUI Very High",
        "Hurricane Category 3+", "Industrial Proximity"
    ]
    PROHIBITED_BUSINESS_TYPES = [
        "cannabis dispensary", "fireworks manufacturing", "ammunition manufacturing",
        "hazardous waste disposal", "adult entertainment", "unlicensed gambling"
    ]

    @classmethod
    def is_api_key_configured(cls) -> bool:
        """Check if a valid API key is available."""
        return bool(cls.GOOGLE_API_KEY and cls.GOOGLE_API_KEY != "your_gemini_api_key_here")


settings = Settings()

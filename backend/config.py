"""
Application Configuration Module

Centralizes all configuration, environment variables, and constants
for the Enterprise Underwriting Platform.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure root .env is loaded reliably locally while respecting Cloud Run env vars
_ROOT_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _ROOT_DIR / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
else:
    load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    """Application-wide settings loaded from environment variables."""

    # --- Google AI ---
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

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
        "High Wildfire Hazard Area"
    ]

    # --- State Restrictions ---
    RESTRICTED_STATES: list = os.getenv("RESTRICTED_STATES", "").split(",") if os.getenv("RESTRICTED_STATES") else []

    # --- Auto-Decline Conditions ---
    PROHIBITED_BUSINESS_TYPES = [
        "fireworks manufacturing", "cannabis dispensary", "gun shop",
        "adult entertainment", "cryptocurrency mining", "hazardous waste disposal",
        "mining", "explosives", "weapons"
    ]

    @classmethod
    def get_api_key(cls) -> str:
        """Dynamically retrieve the active Google/Gemini API key from environment."""
        key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or cls.GOOGLE_API_KEY or ""
        return key.strip().strip("'\"")

    @classmethod
    def is_api_key_configured(cls) -> bool:
        """Check if a valid API key is available."""
        key = cls.get_api_key()
        return bool(key and key != "your_gemini_api_key_here")

    @classmethod
    def call_gemini(cls, prompt: str, system_instruction: str = "") -> str:
        """
        Execute Gemini inference using the official google.genai SDK
        with automatic dynamic model fallback across Gemini 3.7 / 3.5 / 2.5 models.
        """
        if not cls.is_api_key_configured():
            return ""

        api_key = cls.get_api_key()
        last_error = None

        # 1. Primary: Use modern google.genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            candidates = [
                cls.GEMINI_MODEL,
                "gemini-3.7-flash",
                "gemini-3.7-pro",
                "gemini-3.5-flash",
                "gemini-3.5-pro",
                "gemini-3.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ]
            unique_candidates = list(dict.fromkeys([c for c in candidates if c]))

            for model_name in unique_candidates:
                try:
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction
                    ) if system_instruction else None

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config,
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    last_error = e
                    continue

        except Exception as e:
            last_error = e

        # 2. Secondary fallback: Legacy google.generativeai if google.genai is not installed
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as legacy_genai

            legacy_genai.configure(api_key=api_key)
            legacy_candidates = [
                cls.GEMINI_MODEL,
                "gemini-3.7-flash",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ]
            unique_legacy = list(dict.fromkeys([c for c in legacy_candidates if c]))

            for model_name in unique_legacy:
                try:
                    if system_instruction:
                        model = legacy_genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=system_instruction,
                        )
                    else:
                        model = legacy_genai.GenerativeModel(model_name=model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as e:
                    last_error = e
                    continue

        except Exception as e:
            last_error = e

        if last_error:
            logger.warning(f"All Gemini model candidates failed: {last_error}")
        return ""


settings = Settings()

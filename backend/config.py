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

    @classmethod
    def call_gemini(cls, prompt: str, system_instruction: str = "") -> str:
        """
        Execute Gemini inference with automatic dynamic model fallback
        across available Gemini >= 3.5 models.
        """
        if not cls.is_api_key_configured():
            return ""

        import google.generativeai as genai
        genai.configure(api_key=cls.GOOGLE_API_KEY)

        candidates = [
            cls.GEMINI_MODEL,
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ]
        unique_candidates = list(dict.fromkeys(candidates))

        last_error = None
        for model_name in unique_candidates:
            try:
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                else:
                    model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        return ""


settings = Settings()

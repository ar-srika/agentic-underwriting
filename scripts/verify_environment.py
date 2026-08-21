"""
Environment & Dependency Verification Script
"""

import sys
import importlib

REQUIRED_MODULES = [
    "streamlit",
    "plotly",
    "fastapi",
    "uvicorn",
    "pydantic",
    "pdfplumber",
    "dotenv",
]

def verify():
    print("==================================================")
    print("UnderwriteAI — System & Environment Sanity Check")
    print("==================================================")
    print(f"Python Version: {sys.version.split()[0]}")
    
    missing = []
    for mod in REQUIRED_MODULES:
        try:
            importlib.import_module(mod)
            print(f"  [OK] {mod}")
        except ImportError:
            print(f"  [MISSING] {mod}")
            missing.append(mod)

    if missing:
        print(f"\n[ERROR] Missing required packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All core enterprise dependencies verified!")

if __name__ == "__main__":
    verify()

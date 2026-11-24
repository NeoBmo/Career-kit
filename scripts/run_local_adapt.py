#!/usr/bin/env python3
"""Run a local adaptation test using adapt_with_groq and print the result."""

from __future__ import annotations
from scripts.groq_client import adapt_with_groq
import sys
from pathlib import Path
import json

# Ensure project root is discoverable when running this script directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    payload = {
        "name": "Ana",
        "location": "Bogotá",
        "phone": "+57 300 0000000",
        "email": "ana@example.com",
        "title": "Frontend Developer",
        "summary": "Desarrolladora enfocada en productos web.",
        "skills": ["React", "TypeScript", "Next.js"],
        "experiences": [
            {
                "role": "Frontend Developer",
                "dates": "2022 -- 2024",
                "organization": "Acme",
                "details": ["Construí interfaces con React y TypeScript"]
            }
        ],
        "education": []
    }

    result = adapt_with_groq(
        payload, "Frontend Developer Senior. Experiencia con React, TypeScript y Next.js.")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

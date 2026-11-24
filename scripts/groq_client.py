#!/usr/bin/env python3
"""Minimal Groq client + validator + safe fallback to local adapter."""

from __future__ import annotations
import os
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Tuple

from pathlib import Path
from scripts.env_loader import load_env

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
SCHEMAS_DIR = ROOT / "schemas"

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
DEFAULT_API_URL = os.getenv(
    "GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# Basic structural validator (no external deps)


def _validate_structure(obj: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "response is not an object"
    for key in ("objective", "summary", "relevant_skills", "relevant_experiences", "notes"):
        if key not in obj:
            return False, f"missing key: {key}"
    if not isinstance(obj["relevant_skills"], list):
        return False, "relevant_skills is not a list"
    if not isinstance(obj["relevant_experiences"], list):
        return False, "relevant_experiences is not a list"
    # quick check on experiences
    for i, exp in enumerate(obj["relevant_experiences"]):
        if not isinstance(exp, dict):
            return False, f"experience #{i} is not an object"
        for rk in ("role", "organization", "dates", "details", "relevance_score"):
            if rk not in exp:
                return False, f"experience #{i} missing {rk}"
        if not isinstance(exp["details"], list):
            return False, f"experience #{i} details is not a list"
    return True, "ok"


def _read_prompt(name: str, default: str) -> str:
    p = PROMPTS_DIR / name
    if p.exists():
        return p.read_text(encoding="utf-8")
    return default


def _build_messages(system_prompt: str, user_prompt: str) -> list:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def call_groq_raw(system_prompt: str, user_prompt: str, model: str | None = None, temperature: float = 0.2, max_tokens: int = 512, timeout: int = 30) -> dict:
    load_env()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found in environment")

    model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    api_url = os.getenv("GROQ_API_URL", DEFAULT_API_URL)

    body = {
        "model": model,
        "messages": _build_messages(system_prompt, user_prompt),
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_text = resp.read().decode("utf-8")
            try:
                return json.loads(resp_text)
            except json.JSONDecodeError:
                # wrap raw
                return {"raw": resp_text}
    except urllib.error.HTTPError as e:
        # return structured error info to caller
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = ""
        raise RuntimeError(f"HTTPError {e.code}: {e.reason} - {body}") from e
    except Exception as e:
        raise


def adapt_with_groq(payload: dict, job_description: str) -> dict:
    """
    Attempt to adapt profile via Groq. Returns a dict with keys matching schema.
    On failure or invalid output, falls back to local generate_cv.build_adaptation().
    """
    # load prompts
    system_prompt = _read_prompt(
        "system_prompt.txt", "Eres un editor especialista en CVs. Usa solo el payload.")
    template = _read_prompt("user_prompt_template.txt",
                            "Payload:\n{{payload}}\nVacante:\n{{job_description}}")
    user_prompt = template.replace("{{payload}}", json.dumps(
        payload, ensure_ascii=False)).replace("{{job_description}}", job_description or "")

    try:
        resp = call_groq_raw(system_prompt, user_prompt)
    except Exception as e:
        # fallback: local deterministic adapter
        from scripts import generate_cv
        return {
            "objective": generate_cv.build_adaptation(payload, job_description)[0],
            "summary": generate_cv.build_adaptation(payload, job_description)[1],
            "relevant_skills": generate_cv.build_adaptation(payload, job_description)[3],
            "relevant_experiences": generate_cv.build_adaptation(payload, job_description)[2],
            "notes": f"FALLBACK: {str(e)}"
        }

    # try to extract content from common response shapes
    content = None
    if isinstance(resp, dict):
        # OpenAI-compatible: choices[0].message.content or choices[0].text
        choices = resp.get("choices")
        if choices and isinstance(choices, list):
            first = choices[0]
            # nested structure
            msg = first.get("message") or first.get("delta") or {}
            content = msg.get("content") or first.get("text")
        else:
            # maybe resp contains 'raw' with text
            content = resp.get("raw")
    if not content:
        # invalid response, fallback
        from scripts import generate_cv
        return {
            "objective": generate_cv.build_adaptation(payload, job_description)[0],
            "summary": generate_cv.build_adaptation(payload, job_description)[1],
            "relevant_skills": generate_cv.build_adaptation(payload, job_description)[3],
            "relevant_experiences": generate_cv.build_adaptation(payload, job_description)[2],
            "notes": "FALLBACK: empty or unparseable response from Groq"
        }

    # try parse content as JSON
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # try to find first JSON substring
        import re
        m = re.search(r"\{.*\}", content, flags=re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None
        else:
            parsed = None

    if not parsed:
        from scripts import generate_cv
        return {
            "objective": generate_cv.build_adaptation(payload, job_description)[0],
            "summary": generate_cv.build_adaptation(payload, job_description)[1],
            "relevant_skills": generate_cv.build_adaptation(payload, job_description)[3],
            "relevant_experiences": generate_cv.build_adaptation(payload, job_description)[2],
            "notes": "FALLBACK: Groq returned non-JSON or unparsable content"
        }

    ok, msg = _validate_structure(parsed)
    if not ok:
        from scripts import generate_cv
        return {
            "objective": generate_cv.build_adaptation(payload, job_description)[0],
            "summary": generate_cv.build_adaptation(payload, job_description)[1],
            "relevant_skills": generate_cv.build_adaptation(payload, job_description)[3],
            "relevant_experiences": generate_cv.build_adaptation(payload, job_description)[2],
            "notes": f"FALLBACK: validation failed: {msg}"
        }

    # success
    return parsed

#!/usr/bin/env python3
"""Cliente mínimo de Groq: pide la adaptación y valida la respuesta. Sin respaldo propio."""

from __future__ import annotations
import os
import json
import re
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

class GroqResponseError(ValueError):
    """Groq respondió, pero no con algo que se pueda usar."""


def _index_list(obj: Dict[str, Any], key: str, size: int) -> Tuple[bool, str]:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        return False, f"{key} debe ser una lista no vacía"
    # bool es subclase de int: se descarta para que `true` no valga como 1.
    if any(isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < size for i in value):
        return False, f"{key} tiene un índice fuera de rango"
    if len(set(value)) != len(value):
        return False, f"{key} repite un índice"
    return True, "ok"


def _validate_structure(obj: Dict[str, Any], payload: Dict[str, Any]) -> Tuple[bool, str]:
    """Comprueba la forma de la respuesta y que los índices existan en el payload."""
    if not isinstance(obj, dict):
        return False, "la respuesta no es un objeto"
    for key in ("summary", "experience_order", "skills_order", "notes"):
        if key not in obj:
            return False, f"falta la clave {key}"
    summary = obj["summary"]
    if not isinstance(summary, str) or not summary.strip() or summary.strip().upper() == "NO_INFO":
        return False, "summary está vacío"
    if not isinstance(obj["notes"], str):
        return False, "notes no es una cadena"
    for key, source in (("experience_order", "experiences"), ("skills_order", "skills")):
        ok, msg = _index_list(obj, key, len(payload.get(source, [])))
        if not ok:
            return False, msg
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
        raise RuntimeError("No se encontró GROQ_API_KEY en el entorno")

    model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    api_url = os.getenv("GROQ_API_URL", DEFAULT_API_URL)
    # La clave viaja en el encabezado: nunca se envía por http:// ni a otro esquema.
    if not api_url.startswith("https://"):
        raise RuntimeError("GROQ_API_URL debe empezar por https://; no se envió nada a Groq")

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
    """Pide a Groq la adaptación y devuelve {summary, experience_order, skills_order, notes}.

    No hay respaldo aquí: si falla la red, falta la clave o la respuesta no sirve, lanza
    una excepción. Quien llama (generate_cv) decide usar la adaptación local y marcar FALLBACK.
    """
    system_prompt = _read_prompt(
        "system_prompt.txt", "Eres un editor especialista en CVs. Usa solo el payload.")
    template = _read_prompt("user_prompt_template.txt",
                            "Payload:\n{{payload}}\nVacante:\n{{job_description}}")
    user_prompt = template.replace("{{payload}}", json.dumps(
        payload, ensure_ascii=False)).replace("{{job_description}}", job_description or "")

    resp = call_groq_raw(system_prompt, user_prompt)

    # OpenAI-compatible: choices[0].message.content; si no, el texto crudo.
    content = None
    choices = resp.get("choices") if isinstance(resp, dict) else None
    if choices and isinstance(choices, list):
        first = choices[0]
        msg = first.get("message") or first.get("delta") or {}
        content = msg.get("content") or first.get("text")
    elif isinstance(resp, dict):
        content = resp.get("raw")
    if not content:
        raise GroqResponseError("respuesta vacía de Groq")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # Algunos modelos envuelven el JSON en texto: se busca el primer objeto.
        m = re.search(r"\{.*\}", content, flags=re.S)
        try:
            parsed = json.loads(m.group(0)) if m else None
        except json.JSONDecodeError:
            parsed = None
    if parsed is None:
        raise GroqResponseError("Groq no devolvió JSON legible")

    ok, msg = _validate_structure(parsed, payload)
    if not ok:
        raise GroqResponseError(f"respuesta inválida: {msg}")
    return parsed

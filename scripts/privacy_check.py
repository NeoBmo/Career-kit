#!/usr/bin/env python3
"""Comprobación de privacidad: busca correos y teléfonos reales en archivos versionados.

Uso: py -m scripts.privacy_check

Recorre `git ls-files`, salta binarios y falla con código 1 si encuentra un correo
que no sea de example.com ni noreply, o un teléfono de 10 o más dígitos que no sea
el ficticio +00 000 000 0000. Informa archivo y línea.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BINARY_EXTENSIONS = {".ttf", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico"}
ALLOWED_EMAIL_DOMAIN = "example.com"
ALLOWED_PHONE_DIGITS = "000000000000"  # +00 000 000 0000

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Candidato a teléfono: dígitos con separadores; luego se cuentan sólo los dígitos.
PHONE_RE = re.compile(r"(?<!\w)(\+?\d[\d\s().-]{8,}\d)(?!\w)")


def check_line(line: str, lineno: int = 1) -> list[dict[str, object]]:
    """Devuelve los hallazgos de una línea: cada uno con line, type, value y message."""
    findings: list[dict[str, object]] = []
    for match in EMAIL_RE.finditer(line):
        email = match.group(0)
        domain = email.rsplit("@", 1)[-1].lower()
        if domain != ALLOWED_EMAIL_DOMAIN and "noreply" not in email.lower():
            findings.append({"line": lineno, "type": "email", "value": email,
                             "message": f"correo no permitido: {email}"})
    for match in PHONE_RE.finditer(line):
        raw = match.group(1).strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        if len(digits) >= 10 and digits != ALLOWED_PHONE_DIGITS:
            findings.append({"line": lineno, "type": "phone", "value": raw,
                             "message": f"teléfono no permitido: {raw}"})
    return findings


def check_text(text: str) -> list[dict[str, object]]:
    """Devuelve los hallazgos de un bloque de texto, con su número de línea."""
    findings: list[dict[str, object]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        findings.extend(check_line(line, lineno))
    return findings


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                            encoding="utf-8", check=True)
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    failed = False
    for rel in tracked_files():
        path = Path(rel)
        if path.suffix.lower() in BINARY_EXTENSIONS or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for finding in check_text(content):
            failed = True
            print(f"{rel}:{finding['line']}: {finding['message']}")
    print("Comprobación de privacidad: " + ("FALLA" if failed else "OK"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

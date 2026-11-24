#!/usr/bin/env python3
"""Comprobación ATS de un PDF: texto extraíble y keywords presentes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path


def normalize(text: str) -> str:
    """Normaliza texto: sin tildes, en minúsculas y sin espacios repetidos."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def check_text(text: str, keywords: list[str]) -> dict:
    """Comprueba el texto extraído: caracteres y keywords presentes."""
    normalized_text = normalize(text)
    found_keywords: list[str] = []
    missing_keywords: list[str] = []
    for keyword in keywords:
        normalized_keyword = normalize(keyword)
        pattern = r"(?<![0-9a-z])" + re.escape(normalized_keyword) + r"(?![0-9a-z])"
        if re.search(pattern, normalized_text):
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    chars = len(text)
    ok = chars >= 200 and not missing_keywords
    return {
        "chars": chars,
        "missing_keywords": missing_keywords,
        "found_keywords": found_keywords,
        "ok": ok,
    }


def _load_keywords(args: argparse.Namespace) -> list[str]:
    keywords: list[str] = []
    if args.keywords:
        keywords.extend(part.strip() for part in args.keywords.split(","))
    if args.keywords_file:
        file_path = Path(args.keywords_file)
        content = file_path.read_text(encoding="utf-8")
        for part in re.split(r"[,\n]", content):
            keywords.append(part.strip())
    return [keyword for keyword in keywords if keyword]


def _extract_text(pdf_path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if pdftotext is None:
        raise FileNotFoundError("pdftotext")
    result = subprocess.run(
        [pdftotext, "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = result.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        raise RuntimeError(stderr.strip() or "pdftotext falló")
    stdout = result.stdout
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    return stdout


def _print_report(result: dict) -> None:
    print("Comprobación ATS")
    print(f"- Caracteres extraídos: {result['chars']}")
    found = ", ".join(result["found_keywords"]) or "(ninguna)"
    missing = ", ".join(result["missing_keywords"]) or "(ninguna)"
    print(f"- Keywords encontradas: {found}")
    print(f"- Keywords faltantes: {missing}")
    if result["ok"]:
        print("\nResultado: OK")
    else:
        print("\nResultado: FALLA")
        if result["chars"] < 200:
            print("  El PDF tiene menos de 200 caracteres: un ATS no puede leerlo.")
        if result["missing_keywords"]:
            print("  Faltan keywords del perfil en el texto.")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Comprueba si un PDF de CV es legible para un ATS.")
    parser.add_argument("pdf", help="Ruta al archivo PDF")
    parser.add_argument("--keywords", default=None,
                        help="Keywords separadas por comas")
    parser.add_argument("--keywords-file", default=None,
                        help="Archivo con keywords (una por línea o separadas por comas)")
    parser.add_argument("--json", action="store_true",
                        help="Imprime el resultado en JSON")
    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"El archivo no existe: {pdf_path}", file=sys.stderr)
        return 2

    if shutil.which("pdftotext") is None:
        print("pdftotext no está instalado: instala poppler-utils",
              file=sys.stderr)
        return 2

    try:
        text = _extract_text(pdf_path)
    except (FileNotFoundError, RuntimeError) as error:
        if str(error) == "pdftotext":
            print("pdftotext no está instalado: instala poppler-utils",
                  file=sys.stderr)
            return 2
        print(f"Error al extraer texto: {error}", file=sys.stderr)
        return 2

    keywords = _load_keywords(args)
    result = check_text(text, keywords)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        _print_report(result)

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

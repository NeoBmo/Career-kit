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

ROOT = Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    """Normaliza texto: sin tildes, en minúsculas y sin espacios repetidos."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def check_order(text: str, sections: list[str]) -> tuple[bool, list[str]]:
    """Comprueba que los títulos de sección aparezcan, cada uno en su línea, en el orden dado.

    Un PDF con el texto desordenado (columnas mezcladas, capas) deja los títulos en otro
    orden o no los deja solos en una línea. Devuelve (orden_ok, títulos_no_encontrados).
    """
    lines = [normalize(line) for line in text.splitlines()]
    position = -1
    missing: list[str] = []
    in_order = True
    for title in sections:
        wanted = normalize(title)
        found = next((i for i, line in enumerate(lines) if line == wanted), None)
        if found is None:
            missing.append(title)
        elif found < position:
            in_order = False
        else:
            position = found
    return in_order and not missing, missing


def check_text(text: str, keywords: list[str], sections: list[str] | None = None) -> dict:
    """Comprueba el texto extraído: caracteres, keywords presentes y, si se pasan, el orden."""
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
    order_ok, missing_sections = check_order(text, sections) if sections else (True, [])
    ok = chars >= 200 and not missing_keywords and order_ok
    return {
        "chars": chars,
        "missing_keywords": missing_keywords,
        "found_keywords": found_keywords,
        "order_ok": order_ok,
        "missing_sections": missing_sections,
        "ok": ok,
    }


def section_titles(lang: str) -> list[str]:
    """Títulos de sección de la variante, en el orden en que render.py los escribe."""
    source = (ROOT / "lang" / f"{lang}.tex").read_text(encoding="utf-8")
    titles = []
    for label in ("LblProfile", "LblExperience", "LblSkills", "LblEducation"):
        match = re.search(r"\\newcommand\{\\" + label + r"\}\{([^}]*)\}", source)
        if match:
            titles.append(match.group(1))
    return titles


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
    print(f"- Orden de las secciones: {'OK' if result['order_ok'] else 'FALLA'}")
    if result["ok"]:
        print("\nResultado: OK")
    else:
        print("\nResultado: FALLA")
        if result["chars"] < 200:
            print("  El PDF tiene menos de 200 caracteres: un ATS no puede leerlo.")
        if result["missing_keywords"]:
            print("  Faltan keywords del perfil en el texto.")
        if not result["order_ok"]:
            print("  Las secciones no aparecen en el orden esperado: el texto está desordenado.")
            if result["missing_sections"]:
                print(f"  Títulos no encontrados: {', '.join(result['missing_sections'])}")


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
    parser.add_argument("--sections", default=None,
                        help='Títulos de sección en el orden esperado, p. ej. "Perfil,Experiencia,Habilidades,Educación"')
    parser.add_argument("--lang", default=None,
                        help="Deriva los títulos de sección de lang/<lang>.tex")
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
    sections = None
    if args.sections:
        sections = [part.strip() for part in args.sections.split(",") if part.strip()]
    elif args.lang:
        try:
            sections = section_titles(args.lang)
        except OSError:
            print(f"No existe lang/{args.lang}.tex", file=sys.stderr)
            return 2
    result = check_text(text, keywords, sections)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        _print_report(result)

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

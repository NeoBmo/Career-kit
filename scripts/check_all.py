#!/usr/bin/env python3
"""Comprueba el ATS de todas las variantes de una persona.

Uso: py -m scripts.check_all content/<persona>

Para cada variante de content/<persona>/cv.json ejecuta la comprobación ATS
(scripts.ats_check) sobre builds/<persona>/out/cv-<lang>-<profile>.pdf con las
keywords de ese perfil e idioma. Imprime un resumen en español y sale con 1 si
alguna falla.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ats_check import _extract_text, check_text
from scripts.cv_model import CvError, load_cv, text


def _keywords(cv: dict, profile: str, lang: str) -> list[str]:
    profile_data = cv["profiles"][profile]
    kw = profile_data["keywords"]
    # keywords puede ser lista (un idioma) o dict lang->lista
    if isinstance(kw, dict):
        kw = kw[lang]
    if callable(getattr(kw, "__call__", None)):
        kw = text(kw, lang)
    return list(kw)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Comprueba el ATS de todas las variantes de una persona.")
    parser.add_argument("person", help="Carpeta de la persona, p. ej. content/example")
    args = parser.parse_args(argv)

    person_dir = Path(args.person)
    basename = person_dir.name
    out_dir = Path("builds") / basename / "out"

    try:
        cv = load_cv(person_dir / "cv.json")
    except (CvError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    variants = cv["variants"]
    total = len(variants)
    failed = 0
    results: list[tuple[str, bool, int, list[str]]] = []

    for variant in variants:
        lang = variant["lang"]
        profile = variant["profile"]
        name = f"cv-{lang}-{profile}"
        pdf_path = out_dir / f"{name}.pdf"

        if not pdf_path.exists():
            print(f"{name}: FALLA (no existe el PDF {pdf_path})")
            failed += 1
            results.append((name, False, 0, ["PDF no encontrado"]))
            continue

        try:
            extracted = _extract_text(pdf_path)
        except Exception as error:  # noqa: BLE001
            print(f"{name}: FALLA (error al extraer texto: {error})")
            failed += 1
            results.append((name, False, 0, [str(error)]))
            continue

        keywords = _keywords(cv, profile, lang)
        result = check_text(extracted, keywords)
        ok = bool(result["ok"]) if isinstance(result, dict) else bool(result)
        missing = result.get("missing_keywords", []) if isinstance(result, dict) else []
        chars = result.get("chars", len(extracted)) if isinstance(result, dict) else len(extracted)

        status = "OK" if ok else "FALLA"
        print(f"{name}: {status} ({chars} caracteres, {len(missing)} keywords faltantes)")
        if missing:
            print(f"  Keywords faltantes: {', '.join(missing)}")
        if not ok:
            failed += 1
        results.append((name, ok, chars, missing))

    print()
    passed = total - failed
    print(f"Resumen: {passed}/{total} variantes OK")
    if failed:
        print(f"{failed} variante(s) fallaron la comprobación ATS.")
        return 1
    print("Todas las variantes pasan la comprobación ATS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

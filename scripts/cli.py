#!/usr/bin/env python3
"""Menú de terminal para generar y adaptar hojas de vida.

Uso: py -m scripts.cli
"""

from __future__ import annotations

import sys

from scripts import generate_cv

DEFAULT_PERSON = "content/example"
DEFAULT_VARIANT = "es/software-developer"


def ask(prompt: str, default: str = "") -> str:
    value = input(prompt).strip()
    return value or default


def ask_job() -> str:
    """Lee la vacante línea a línea hasta una línea vacía (pegar varias líneas con input() no sirve)."""
    print("Pega el texto de la vacante y termina con una línea vacía:")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip() and lines:
            break
        if line.strip():
            lines.append(line)
    return "\n".join(lines)


def run() -> int:
    # La consola de Windows usa cp1252 y no pinta bien acentos ni símbolos.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    print("\nCAREER KIT")
    print("1) Generar mis hojas de vida")
    print("2) Adaptar a una vacante")
    print("3) Salir")
    choice = ask("Elige una opción [1]: ", "1")

    if choice == "3":
        print("Hasta pronto.")
        return 0
    if choice == "1":
        person = ask(f"Carpeta de tu hoja de vida [{DEFAULT_PERSON}]: ", DEFAULT_PERSON)
        return generate_cv.main([person])
    if choice == "2":
        person = ask(f"Carpeta de tu hoja de vida [{DEFAULT_PERSON}]: ", DEFAULT_PERSON)
        variant = ask(f"Variante (idioma/perfil) [{DEFAULT_VARIANT}]: ", DEFAULT_VARIANT)
        job = ask_job()
        if not job:
            print("No se recibió una vacante.", file=sys.stderr)
            return 1
        return generate_cv.main([person, "--variant", variant, "--job-description", job])
    print("Opción no válida.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(run())

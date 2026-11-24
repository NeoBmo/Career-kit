#!/usr/bin/env python3
"""A simple terminal UI for the CV generator."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from scripts.env_loader import load_env
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cv-data.json"
OUTPUT_PATH = ROOT / "builds" / "generated-cv.tex"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_box(title: str, body: str) -> None:
    border = "═" * (len(title) + 4)
    print("\n┌" + border + "┐")
    print("│  " + title + "  │")
    print("└" + border + "┘")
    print(body)


def ask(prompt: str, default: Optional[str] = None) -> str:
    value = input(prompt).strip()
    if value:
        return value
    if default is not None:
        return default
    return ""


def generate(*extra: str) -> None:
    # Se lanza como módulo (-m) desde la raíz: por ruta directa, Python no encuentra
    # el paquete `scripts` y el import de generate_cv falla.
    import subprocess
    subprocess.run(
        [sys.executable, "-m", "scripts.generate_cv",
         "--input", str(DATA_PATH), "--output", str(OUTPUT_PATH), *extra],
        check=True,
        cwd=str(ROOT),
    )


def run() -> None:
    # La consola de Windows usa cp1252 y no sabe pintar los bordes del menú.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    load_env()
    clear_screen()
    print_box("CAREER KIT AI",
              "[1] Generar CV\n[2] Adaptar a una vacante\n[3] Salir")
    choice = ask("Selecciona una opción: ", "1")

    if choice == "3":
        print("\nHasta pronto.\n")
        return

    if not DATA_PATH.exists():
        print("No existe el archivo de datos.")
        return

    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    if choice == "2":
        job_description = ask("Pega la descripción de la vacante: ")
        if not job_description:
            print("No se recibió una vacante.")
            return
        print("\nAdaptando propuesta...\n")
        generate("--job-description", job_description)
        print("Listo. Revisa el archivo generado y la propuesta JSON.")
        return

    print("\nGenerando CV base...\n")
    generate()
    print("Listo. El CV base fue generado.")


if __name__ == "__main__":
    run()

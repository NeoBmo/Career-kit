#!/usr/bin/env python3
"""Render one complete .tex per variant of a person's cv.json.

Uso: py -m scripts.render content/<persona> [--out builds/<persona>]

Cada archivo reproduce la estructura de main.tex (perfil, experiencia, habilidades,
educación y pie «Conoce más»). Las etiquetas salen de lang/<lang>.tex y el diseño de
styles/modern.tex; las rutas son relativas a la raíz del repo, desde donde compila
build.sh.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from scripts.cv_model import CvError, load_cv, text

ROOT = Path(__file__).resolve().parents[1]

# Un solo recorrido por carácter: así el `{}` que añade \textbackslash{} no se
# vuelve a escapar, como pasaría con reemplazos encadenados.
_TEXT_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

# Dentro del primer argumento de \href sólo `%` y `#` rompen la compilación.
_URL_ESCAPES = {"%": r"\%", "#": r"\#"}


def escape(value: str) -> str:
    """Escapa texto para LaTeX. Guiones largos y acentos UTF-8 quedan tal cual."""
    return "".join(_TEXT_ESCAPES.get(char, char) for char in value)


def escape_url(value: str) -> str:
    """Prepara una URL (o mailto:) para el primer argumento de \\href."""
    return "".join(_URL_ESCAPES.get(char, char) for char in value)


def href(url: str, label: str) -> str:
    return rf"\href{{{escape_url(url)}}}{{{escape(label)}}}"


def dates(start: str | None, end: str | None) -> str:
    """«inicio -- fin»; fin null es \\LblPresent y sin inicio queda sólo el fin."""
    end_tex = escape(end) if end else r"\LblPresent"
    return f"{escape(start)} -- {end_tex}" if start else end_tex


def render_variant(cv: dict[str, Any], lang: str, profile_name: str) -> str:
    """Devuelve el .tex completo de una variante. El cv ya debe estar validado."""
    person, more = cv["person"], cv["more"]
    profile = cv["profiles"][profile_name]

    name = escape(person["name"])
    title = escape(text(profile["title"], lang))
    keywords = escape(", ".join(text(profile["keywords"], lang)))
    contact = (rf"{escape(text(person['location'], lang))}\ \textbar\ "
               rf"{escape(person['phone'])}\ \textbar\ "
               + href(f"mailto:{person['email']}", person["email"]))

    experience: list[str] = []
    for entry in cv["experience"]:
        experience.append(
            rf"\ckEntry{{{escape(text(entry['role'], lang))}}}"
            rf"{{{dates(entry['start'], entry['end'])}}}"
            rf"{{{escape(text(entry['organization'], lang))}}}{{}}")
        experience.append(r"\begin{ckitems}")
        experience.extend(rf"  \item {escape(item)}" for item in text(entry["highlights"], lang))
        experience.append(r"\end{ckitems}")

    skills = [r"\begin{ckitems}"]
    skills.extend(
        rf"  \item \textbf{{{escape(text(group['label'], lang))}:}} {escape(text(group['items'], lang))}"
        for group in cv["skills"])
    skills.append(r"\end{ckitems}")

    # Como en main.tex, cada entrada va seguida de su párrafo de detalles. Las entradas
    # se separan con una línea en blanco: sin ese \par, el párrafo seguiría abierto y
    # la \ckEntry siguiente quedaría en la misma línea, con la fecha fuera de la página.
    education: list[str] = []
    for entry in cv["education"]:
        education.append(
            rf"\ckEntry{{{escape(text(entry['title'], lang))}}}"
            rf"{{{dates(entry['start'], entry['end'])}}}"
            rf"{{{escape(text(entry['organization'], lang))}}}{{}}"
            "\n" + escape(text(entry["details"], lang)))

    summary = escape(text(profile["summary"], lang))
    more_link = href(more["url"], text(more["label"], lang))
    nl = "\n"

    return rf"""% Generado por scripts/render.py desde cv.json. No editar a mano.
\documentclass[10pt]{{article}}

% --- Idioma (etiquetas de la plantilla) ---
\input{{lang/{lang}.tex}}

% --- Estilo (diseño visual) ---
\input{{styles/modern.tex}}

% --- Metadatos del PDF (útil para ATS que leen metadata) ---
\hypersetup{{
  pdftitle={{{name} - {title}}},
  pdfauthor={{{name}}},
  pdfsubject={{{title}}},
  pdfkeywords={{{keywords}}}
}}

\begin{{document}}

% ---------- Encabezado ----------
\ckHeader{{{name}}}{{{title}}}{{{contact}}}

\vspace{{3pt}}

% ---------- Perfil ----------
\section*{{\LblProfile}}
{summary}

% ---------- Experiencia ----------
\section*{{\LblExperience}}
{nl.join(experience)}

% ---------- Habilidades ----------
\section*{{\LblSkills}}
{nl.join(skills)}

% ---------- Educación ----------
\section*{{\LblEducation}}
{(nl + nl).join(education)}

\begin{{center}}
  {{\footnotesize\color{{ckSubtle}}\LblMore\ ---\ {more_link}}}
\end{{center}}

\end{{document}}
"""


def render_person(person_dir: str | Path, out_dir: str | Path) -> list[Path]:
    """Valida content/<persona>/cv.json y escribe cv-<lang>-<profile>.tex por variante."""
    cv = load_cv(Path(person_dir) / "cv.json")
    missing = [f"variants[{i}].lang: no existe lang/{v['lang']}.tex"
               for i, v in enumerate(cv["variants"]) if not (ROOT / "lang" / f"{v['lang']}.tex").is_file()]
    if missing:
        raise CvError(missing)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for variant in cv["variants"]:
        lang, profile = variant["lang"], variant["profile"]
        path = out / f"cv-{lang}-{profile}.tex"
        # newline="\n": el .tex queda con LF también en Windows.
        path.write_text(render_variant(cv, lang, profile), encoding="utf-8", newline="\n")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render one .tex per variant of a cv.json")
    parser.add_argument("person", help="Carpeta de la persona, p. ej. content/example")
    parser.add_argument("--out", help="Carpeta de salida (por defecto builds/<persona>)")
    args = parser.parse_args(argv)

    person_dir = Path(args.person)
    out_dir = Path(args.out) if args.out else Path("builds") / person_dir.name
    try:
        written = render_person(person_dir, out_dir)
    except (CvError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())

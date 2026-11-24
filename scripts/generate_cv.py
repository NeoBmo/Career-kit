#!/usr/bin/env python3
"""Adapta una variante de cv.json a una vacante y la renderiza con scripts/render.py.

Uso:
  py -m scripts.generate_cv content/<persona> --variant es/software-developer \
      (--job-description "..." | --job-file vacante.txt) [--yes]

Sin vacante no adapta: renderiza todas las variantes, igual que `scripts.render`.
La adaptación sólo cambia el resumen y el orden o la selección de experiencias y de
grupos de habilidades; el .tex sale del MISMO renderizador (RF-05). Las notas de
revisión y la marca FALLBACK van sólo a la propuesta JSON y a la consola (RF-06).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from scripts.cv_model import CvError, load_cv, text
from scripts.env_loader import load_env
from scripts.groq_client import adapt_with_groq
from scripts.render import ROOT, render_person, render_variant

GROQ_NOTICE = """\
AVISO DE PRIVACIDAD (Groq)
Para adaptar tu hoja de vida con IA, el contenido de esta variante (perfil, experiencia
y habilidades, con los nombres de las empresas) y el texto de la vacante se enviarán a Groq,
un servicio de terceros que no controlamos, con tu propia clave de API. Groq lo
trata según su política de privacidad: https://groq.com/privacy-policy
Tu teléfono, tu correo, tu nombre y tu ubicación NO se envían: la IA no los necesita.
Si no aceptas, se usa la adaptación local, que no sale de tu equipo."""


# ---------- Vista de la variante ----------

def _span(entry: dict[str, Any]) -> str:
    end = entry["end"] or "actual"
    return f"{entry['start']} -- {end}" if entry["start"] else end


def variant_view(cv: dict[str, Any], lang: str, profile_name: str) -> dict[str, Any]:
    """Lo que la IA puede ver: textos de un idioma, sin teléfono, correo, nombre ni ubicación.

    Las experiencias y las habilidades llevan su `index` en cv.json: la IA responde con
    índices y así no puede inventar entradas.
    """
    profile = cv["profiles"][profile_name]
    return {
        "language": lang,
        "title": text(profile["title"], lang),
        "summary": text(profile["summary"], lang),
        "keywords": text(profile["keywords"], lang),
        "experiences": [
            {"index": i, "role": text(e["role"], lang), "organization": text(e["organization"], lang),
             "dates": _span(e), "highlights": text(e["highlights"], lang)}
            for i, e in enumerate(cv["experience"])],
        "skills": [
            {"index": i, "label": text(g["label"], lang), "items": text(g["items"], lang)}
            for i, g in enumerate(cv["skills"])],
    }


# ---------- Adaptación local ----------

def _terms(view: dict[str, Any]) -> list[str]:
    """Términos del CV que se buscan en la vacante: keywords y habilidades sueltas."""
    found: dict[str, str] = {}
    candidates = list(view["keywords"])
    for group in view["skills"]:
        candidates.extend(re.split(r"[,()]", group["items"]))
    for term in candidates:
        term = term.strip()
        if len(term) >= 2:
            found.setdefault(term.lower(), term)
    return list(found.values())


def _mentions(haystack: str, term: str) -> bool:
    """El término aparece como palabra completa (así «SQL» no coincide con «PostgreSQL»)."""
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", haystack, flags=re.IGNORECASE) is not None


def adapt_locally(view: dict[str, Any], job: str) -> dict[str, Any]:
    """Adaptación determinista sin red. Devuelve la misma forma que Groq.

    Sólo reordena y selecciona con coincidencias de palabras entre el CV y la vacante;
    el resumen sólo añade una frase con términos que ya están en el CV.
    """
    matched = [t for t in _terms(view) if _mentions(job, t)]

    def score(texts: list[str]) -> int:
        blob = " ".join(texts)
        return sum(1 for t in matched if _mentions(blob, t))

    experiences = [(score([e["role"], *e["highlights"]]), e["index"]) for e in view["experiences"]]
    relevant = [p for p in experiences if p[0] > 0] or experiences
    # sorted es estable: a igual puntaje se conserva el orden original.
    experience_order = [i for _, i in sorted(relevant, key=lambda p: -p[0])]

    skills = [(score([g["label"], g["items"]]), g["index"]) for g in view["skills"]]
    skills_order = [i for _, i in sorted(skills, key=lambda p: -p[0])]

    summary = view["summary"]
    if matched:
        shown = ", ".join(matched[:6])
        summary += (f" Experiencia relacionada con la vacante: {shown}." if view["language"] == "es"
                    else f" Experience related to the role: {shown}.")
    notes = ("Adaptación local: se reordenó por coincidencia de palabras con la vacante."
             + (f" Términos encontrados: {', '.join(matched)}." if matched
                else " No se encontraron términos del CV en la vacante; se conservó el orden."))
    return {"summary": summary, "experience_order": experience_order,
            "skills_order": skills_order, "notes": notes}


# ---------- Aplicar y renderizar ----------

def apply_adaptation(cv: dict[str, Any], profile_name: str, result: dict[str, Any]) -> dict[str, Any]:
    """Copia del cv con el resumen nuevo y las experiencias y habilidades en su nuevo orden.

    El texto queda como cadena simple; render.py lo escapa para LaTeX igual que el resto,
    así que lo que traiga la IA (`&`, `%`) no rompe la compilación.
    """
    adapted = copy.deepcopy(cv)
    adapted["profiles"][profile_name]["summary"] = result["summary"]
    adapted["experience"] = [cv["experience"][i] for i in result["experience_order"]]
    adapted["skills"] = [cv["skills"][i] for i in result["skills_order"]]
    return adapted


def _is_interactive() -> bool:
    return sys.stdin is not None and sys.stdin.isatty()


def confirm_send(assume_yes: bool) -> bool:
    """RF-15: avisa de que el CV sale a Groq y pide «s». Sin --yes ni terminal, no envía."""
    print(GROQ_NOTICE)
    if assume_yes:
        print("Se envía porque pasaste --yes.")
        return True
    if not _is_interactive():
        print("Entrada no interactiva y sin --yes: no se envía nada a Groq.")
        return False
    try:
        answer = input("¿Enviar a Groq? [s/N]: ")
    except EOFError:
        return False
    return answer.strip().lower() == "s"


def _label(entry: dict[str, Any], lang: str) -> str:
    return f"{text(entry['role'], lang)} @ {text(entry['organization'], lang)}"


def _proposal(cv: dict[str, Any], lang: str, profile: str, view: dict[str, Any], result: dict[str, Any],
              source: str, fallback: bool, reason: str | None, tex: Path) -> dict[str, Any]:
    kept = result["experience_order"]
    notes = [result["notes"]] if result.get("notes") else []
    notes.append("Revisa el resumen y el orden antes de enviar la hoja de vida.")
    return {
        "variant": f"{lang}/{profile}",
        "fallback": fallback,
        "fallback_reason": reason,
        "source": source,
        "tex": tex.as_posix(),
        "changes": {
            "summary": {"before": view["summary"], "after": result["summary"]},
            "experience": [_label(cv["experience"][i], lang) for i in kept],
            "experience_dropped": [_label(e, lang) for i, e in enumerate(cv["experience"]) if i not in kept],
            "skills": [text(cv["skills"][i]["label"], lang) for i in result["skills_order"]],
        },
        "review_notes": notes,
    }


def adapt_person(person_dir: Path, variant: str, job: str, out_dir: Path, assume_yes: bool = False) -> Path:
    """Adapta una variante a la vacante y escribe el .tex y su propuesta JSON. Devuelve el .tex."""
    cv = load_cv(person_dir / "cv.json")
    lang, _, profile = variant.partition("/")
    if not any(v["lang"] == lang and v["profile"] == profile for v in cv["variants"]):
        valid = ", ".join(f"{v['lang']}/{v['profile']}" for v in cv["variants"])
        raise CvError([f"--variant: '{variant}' no existe en cv.json (variantes: {valid})"])
    if not (ROOT / "lang" / f"{lang}.tex").is_file():
        raise CvError([f"--variant: no existe lang/{lang}.tex"])

    view = variant_view(cv, lang, profile)
    load_env()
    source, fallback, reason = "local", False, None
    result: dict[str, Any] | None = None

    if not os.getenv("GROQ_API_KEY"):
        print("Aviso: no hay GROQ_API_KEY; se usa la adaptación local.")
    elif confirm_send(assume_yes):
        source = "groq"
        try:
            result = adapt_with_groq(view, job)
        except Exception as exc:  # red, clave, HTTP o respuesta inválida: RF-06
            source, fallback, reason = "local", True, f"{type(exc).__name__}: {exc}"
            print(f"FALLBACK: Groq falló ({reason}). Se usa la adaptación local.", file=sys.stderr)
    else:
        print("Se usa la adaptación local; el CV no sale de tu equipo.")

    if result is None:
        result = adapt_locally(view, job)
    adapted = apply_adaptation(cv, profile, result)

    out_dir.mkdir(parents=True, exist_ok=True)
    tex = out_dir / f"cv-{lang}-{profile}-vacante.tex"
    tex.write_text(render_variant(adapted, lang, profile), encoding="utf-8", newline="\n")
    proposal = tex.with_suffix(".proposal.json")
    proposal.write_text(
        json.dumps(_proposal(cv, lang, profile, view, result, source, fallback, reason, tex),
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CV adaptado: {tex.as_posix()}")
    print(f"Propuesta con los cambios y las notas de revisión: {proposal.as_posix()}")
    return tex


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adapta una variante de cv.json a una vacante")
    parser.add_argument("person", help="Carpeta de la persona, p. ej. content/example")
    parser.add_argument("--variant", help="Variante a adaptar, p. ej. es/software-developer")
    job = parser.add_mutually_exclusive_group()
    job.add_argument("--job-description", help="Texto de la vacante")
    job.add_argument("--job-file", help="Archivo de texto con la vacante")
    parser.add_argument("--yes", action="store_true", help="Acepta enviar el CV a Groq sin preguntar")
    parser.add_argument("--out", help="Carpeta de salida (por defecto builds/<persona>)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    person_dir = Path(args.person)
    out_dir = Path(args.out) if args.out else Path("builds") / person_dir.name
    try:
        job = args.job_description
        if args.job_file:
            job = Path(args.job_file).read_text(encoding="utf-8-sig")
        if not job or not job.strip():
            # Sin vacante no se adapta: mismo resultado que `render`.
            for path in render_person(person_dir, out_dir):
                print(path.as_posix())
            return 0
        if not args.variant:
            raise CvError(["--variant: indica la variante a adaptar, p. ej. es/software-developer"])
        adapt_person(person_dir, args.variant, job, out_dir, assume_yes=args.yes)
    except (CvError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

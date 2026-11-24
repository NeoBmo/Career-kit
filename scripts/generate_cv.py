#!/usr/bin/env python3
"""Generate a LaTeX CV from structured JSON data and optionally adapt it to a job description."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from scripts.env_loader import load_env
from scripts.groq_client import adapt_with_groq

REQUIRED_FIELDS = ["name", "location", "phone", "email", "title", "summary"]


def tex_escape(value: str) -> str:
    replacements = {
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
    result = str(value)
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def validate_payload(payload: dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if not payload.get(field):
            raise ValueError(f"Missing required field: {field}")
    if not isinstance(payload.get("experiences", []), list):
        raise ValueError("'experiences' must be a list")
    if not isinstance(payload.get("skills", []), list):
        raise ValueError("'skills' must be a list")
    if not isinstance(payload.get("education", []), list):
        raise ValueError("'education' must be a list")


def _extract_keywords(job_description: str, skills: list[str]) -> list[str]:
    text = job_description.lower()
    return [skill for skill in skills if skill.lower() in text]


def _resolve_text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip() and value.strip().upper() != "NO_INFO":
        return value
    return fallback


def build_adaptation(payload: dict[str, Any], job_description: str | None = None, adaptation_data: dict[str, Any] | None = None) -> tuple[str, str, list[dict[str, Any]], list[str]]:
    summary = payload.get("summary", "")
    skills = payload.get("skills", [])
    title = payload.get("title", "")
    experiences = payload.get("experiences", [])

    if job_description:
        keywords = _extract_keywords(job_description, skills)
        if keywords:
            objective = f"{title} orientado a {', '.join(keywords)} y a la ejecución de soluciones web alineadas con la vacante."
            adapted_summary = f"{summary} Enfocado en {', '.join(keywords)} para responder a las necesidades del puesto."
        else:
            objective = f"{title} orientado a fortalecer la adaptación del perfil a esta vacante."
            adapted_summary = f"{summary} Adaptación orientada a resaltar experiencia relevante y coherente con la vacante."

        adapted_experiences: list[dict[str, Any]] = []
        for experience in experiences:
            detail_text = " ".join(experience.get("details", []))
            score = sum(1 for keyword in keywords if keyword.lower()
                        in detail_text.lower())
            if score > 0:
                adapted_experiences.append(
                    {**experience, "relevance_score": score})

        if not adapted_experiences:
            adapted_experiences = [
                {**experience, "relevance_score": 1} for experience in experiences]

        adapted_skills = [
            skill for skill in skills if skill.lower() in job_description.lower()]
        if not adapted_skills:
            adapted_skills = skills
    else:
        objective = title
        adapted_summary = summary
        adapted_experiences = [{**experience, "relevance_score": 1}
                               for experience in experiences]
        adapted_skills = skills

    if adaptation_data:
        objective = _resolve_text(adaptation_data.get("objective"), objective)
        adapted_summary = _resolve_text(
            adaptation_data.get("summary"), adapted_summary)

        ai_skills = adaptation_data.get("relevant_skills")
        if isinstance(ai_skills, list) and ai_skills:
            adapted_skills = [str(skill) for skill in ai_skills if str(
                skill).strip() and str(skill).strip().upper() != "NO_INFO"]

        ai_experiences = adaptation_data.get("relevant_experiences")
        if isinstance(ai_experiences, list) and ai_experiences:
            adapted_experiences = ai_experiences

    return objective, adapted_summary, adapted_experiences, adapted_skills


def build_latex(payload: dict[str, Any], job_description: str | None = None, adaptation_data: dict[str, Any] | None = None) -> str:
    name = tex_escape(payload["name"])
    location = tex_escape(payload["location"])
    phone = tex_escape(payload["phone"])
    email = tex_escape(payload["email"])
    title = tex_escape(payload["title"])
    summary = tex_escape(payload["summary"])
    keywords = tex_escape(payload.get("keywords", ""))
    objective, adapted_summary, adapted_experiences, adapted_skills = build_adaptation(
        payload, job_description, adaptation_data=adaptation_data)
    objective = tex_escape(objective)
    adapted_summary = tex_escape(adapted_summary)

    review_notes = ""
    if adaptation_data:
        notes = adaptation_data.get("notes")
        if isinstance(notes, str) and notes.strip():
            review_notes = tex_escape(f"Revisar manualmente: {notes}")
        else:
            review_notes = tex_escape("Revisar manualmente antes de exportar.")

    experience_blocks: list[str] = []
    for item in adapted_experiences:
        role = tex_escape(item.get("role", ""))
        dates = tex_escape(item.get("dates", ""))
        organization = tex_escape(item.get("organization", ""))
        details = item.get("details", [])
        block = [
            f"\\ckEntry{{{role}}}{{{dates}}}{{{organization}}}{{}}", "\\begin{ckitems}"]
        for detail in details:
            block.append(f"  \\item {tex_escape(detail)}")
        block.append("\\end{ckitems}")
        experience_blocks.append("\n".join(block))

    skill_items = "\n".join(
        f"  \\item {tex_escape(skill)}" for skill in adapted_skills)

    education_blocks: list[str] = []
    for item in payload.get("education", []):
        title_text = tex_escape(item.get("title", ""))
        dates = tex_escape(item.get("dates", ""))
        organization = tex_escape(item.get("organization", ""))
        details = tex_escape(item.get("details", ""))
        education_blocks.append(
            f"\\ckEntry{{{title_text}}}{{{dates}}}{{{organization}}}{{{details}}}"
        )

    # Las notas de revisión sólo aparecen cuando hubo adaptación a una vacante.
    review_block = f"\\section*{{Review notes}}\n{review_notes}\n" if review_notes else ""

    # Cadena raw (rf): cada comando LaTeX lleva UNA barra. Con dos, LaTeX lee un salto
    # de línea (\\) seguido de texto suelto y el documento no compila.
    # build.sh compila desde la raíz del proyecto, así que las rutas son relativas a ella.
    return rf"""\documentclass[10pt]{{article}}
\input{{styles/modern.tex}}

\newcommand{{\ckName}}{{{name}}}
\newcommand{{\ckLocation}}{{{location}}}
\newcommand{{\ckPhone}}{{{phone}}}
\newcommand{{\ckEmail}}{{{email}}}
\newcommand{{\ckProfileTitle}}{{{title}}}
\newcommand{{\ckKeywords}}{{{keywords}}}

\hypersetup{{
  pdftitle={{{name} - {title}}},
  pdfauthor={{{name}}},
  pdfsubject={{{title}}},
  pdfkeywords={{{keywords}}}
}}

\begin{{document}}

\ckHeader{{{name}}}{{{title}}}{{{location} \textbar\ {phone} \textbar\ \href{{mailto:{email}}}{{{email}}}}}

\vspace{{3pt}}

\section*{{Perfil}}
{adapted_summary}

\section*{{Objetivo profesional}}
{objective}

\section*{{Experiencia}}
{chr(10).join(experience_blocks)}

\section*{{Habilidades}}
\begin{{ckitems}}
{skill_items}
\end{{ckitems}}
{review_block}\section*{{Educación}}
{chr(10).join(education_blocks)}

\end{{document}}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a LaTeX CV from JSON data")
    parser.add_argument("--input", default="data/cv-data.json",
                        help="Path to the JSON input file")
    parser.add_argument("--output", default="builds/generated-cv.tex",
                        help="Path to the generated LaTeX file")
    parser.add_argument("--job-description", default="",
                        help="Optional job description to adapt the CV")
    return parser.parse_args()


def main() -> None:
    load_env()
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    validate_payload(payload)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.job_description:
        proposal_data = adapt_with_groq(payload, args.job_description)
        output_path.write_text(build_latex(
            payload, job_description=args.job_description, adaptation_data=proposal_data), encoding="utf-8")
        proposal_path = output_path.with_suffix(".proposal.json")
        proposal_path.write_text(json.dumps(
            proposal_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Generated proposal summary at {proposal_path}")
    else:
        output_path.write_text(build_latex(
            payload, job_description=args.job_description), encoding="utf-8")

    print(f"Generated CV source at {output_path}")


if __name__ == "__main__":
    main()

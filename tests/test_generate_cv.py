import importlib.util
import os
import unittest
from pathlib import Path
from typing import Any

from scripts.env_loader import load_env

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "generate_cv.py"
SPEC = importlib.util.spec_from_file_location("generate_cv", SCRIPT_PATH)
assert SPEC is not None
generate_cv = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(generate_cv)


class GenerateCvTests(unittest.TestCase):
    def test_load_env_reads_project_root_dotenv(self) -> None:
        env_path = ROOT / ".env"
        backup_content = env_path.read_text(
            encoding="utf-8") if env_path.exists() else None
        os.environ.pop("GROQ_API_KEY", None)

        try:
            env_path.write_text(
                "GROQ_API_KEY=test-key-from-root\n", encoding="utf-8")
            os.chdir(ROOT / "tests")
            load_env()
            self.assertEqual(os.getenv("GROQ_API_KEY"), "test-key-from-root")
        finally:
            if backup_content is None:
                env_path.unlink(missing_ok=True)
            else:
                env_path.write_text(backup_content, encoding="utf-8")
            os.environ.pop("GROQ_API_KEY", None)
            os.chdir(ROOT)

    def test_generates_adapted_objective_from_job_description(self) -> None:
        payload: dict[str, Any] = {
            "name": "Ana",
            "location": "Bogotá",
            "phone": "+00 000 000 0000",
            "email": "ana@example.com",
            "title": "Frontend Developer",
            "summary": "Desarrolladora enfocada en productos web.",
            "skills": ["React", "TypeScript", "Next.js"],
            "experiences": [
                {
                    "role": "Frontend Developer",
                    "dates": "2022 -- 2024",
                    "organization": "Acme",
                    "details": ["Construí interfaces con React y TypeScript"]
                }
            ],
            "education": [],
        }
        job_description = "Frontend Developer Senior. Experiencia con React, TypeScript y Next.js."

        latex = generate_cv.build_latex(
            payload, job_description=job_description)
        objective, summary, adapted_experiences, adapted_skills = generate_cv.build_adaptation(
            payload, job_description)

        self.assertIn("Objetivo profesional", latex)
        self.assertIn("React", latex)
        self.assertIn("TypeScript", latex)
        self.assertIn("productos web", latex)
        self.assertIn("React", objective)
        self.assertIn("TypeScript", summary)
        self.assertEqual(adapted_experiences[0]["organization"], "Acme")
        self.assertIn("React", adapted_skills)

    def test_uses_ai_adaptation_data_when_available(self) -> None:
        payload: dict[str, Any] = {
            "name": "Ana",
            "location": "Bogotá",
            "phone": "+00 000 000 0000",
            "email": "ana@example.com",
            "title": "Frontend Developer",
            "summary": "Desarrolladora enfocada en productos web.",
            "skills": ["React", "TypeScript", "Next.js"],
            "experiences": [
                {
                    "role": "Frontend Developer",
                    "dates": "2022 -- 2024",
                    "organization": "Acme",
                    "details": ["Construí interfaces con React y TypeScript"]
                }
            ],
            "education": [],
        }
        adaptation_data: dict[str, Any] = {
            "objective": "Objetivo alineado con arquitectura frontend y experiencia en React.",
            "summary": "Resumen adaptado por IA para el puesto de frontend senior.",
            "relevant_skills": ["React", "TypeScript"],
            "relevant_experiences": [{
                "role": "Frontend Developer",
                "organization": "Acme",
                "dates": "2022 -- 2024",
                "details": ["Diseñé interfaces y componentes reutilizables con React."],
                "relevance_score": 3
            }],
            "notes": "Adaptado por IA"
        }

        latex = generate_cv.build_latex(
            payload, adaptation_data=adaptation_data)

        self.assertIn("Objetivo alineado con arquitectura frontend", latex)
        self.assertIn("Resumen adaptado por IA", latex)
        self.assertIn("React", latex)
        self.assertIn("TypeScript", latex)
        self.assertIn("componentes reutilizables", latex)

    def test_includes_editorial_review_notes_for_ai_adaptation(self) -> None:
        payload: dict[str, Any] = {
            "name": "Ana",
            "location": "Bogotá",
            "phone": "+00 000 000 0000",
            "email": "ana@example.com",
            "title": "Frontend Developer",
            "summary": "Desarrolladora enfocada en productos web.",
            "skills": ["React", "TypeScript", "Next.js"],
            "experiences": [
                {
                    "role": "Frontend Developer",
                    "dates": "2022 -- 2024",
                    "organization": "Acme",
                    "details": ["Construí interfaces con React y TypeScript"]
                }
            ],
            "education": [],
        }
        adaptation_data: dict[str, Any] = {
            "objective": "Objetivo alineado con la vacante.",
            "summary": "Resumen adaptado por IA.",
            "relevant_skills": ["React"],
            "relevant_experiences": [],
            "notes": "Adaptado por IA"
        }

        latex = generate_cv.build_latex(
            payload, job_description="Frontend Developer", adaptation_data=adaptation_data)

        self.assertIn("Review notes", latex)
        self.assertIn("Revisar manualmente", latex)

    def test_latex_commands_use_a_single_backslash(self) -> None:
        payload: dict[str, Any] = {
            "name": "Ana", "location": "Bogotá", "phone": "+00 000 000 0000",
            "email": "ana@example.com", "title": "Frontend Developer",
            "summary": "Resumen.", "skills": ["React"], "experiences": [], "education": [],
        }

        latex = generate_cv.build_latex(payload)

        # Con dos barras, LaTeX lee un salto de línea y el documento no compila.
        self.assertTrue(latex.startswith("\\documentclass"), latex[:40])
        self.assertNotIn("\\\\section", latex)
        self.assertIn("\\input{styles/modern.tex}", latex)
        # Sin adaptación no hay notas de revisión.
        self.assertNotIn("Review notes", latex)


if __name__ == "__main__":
    unittest.main()

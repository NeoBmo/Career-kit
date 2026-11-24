import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import generate_cv
from scripts.env_loader import load_env

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "content" / "example"
VARIANT = "es/software-developer"
JOB = "Buscamos a alguien con Docker y PostgreSQL para mantener nuestra plataforma."
KEY = {"GROQ_API_KEY": "clave-de-prueba"}
PHONE, EMAIL = "+00 000 000 0000", "alex@example.com"

GROQ_RESULT = {"summary": "Resumen de IA para la vacante.", "experience_order": [1, 0],
               "skills_order": [3, 1], "notes": "Reordené por la vacante."}


def run_main(out: Path, *extra: str, interactive: bool = False, answer: str = "n") -> tuple[int, str, str]:
    """Ejecuta generate_cv.main sin red ni terminal. Devuelve (código, stdout, stderr)."""
    argv = [str(EXAMPLE), "--variant", VARIANT, "--job-description", JOB, "--out", str(out), *extra]
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ, KEY), \
            mock.patch.object(generate_cv, "_is_interactive", return_value=interactive), \
            mock.patch("builtins.input", return_value=answer), \
            contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = generate_cv.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class GenerateCvTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.out = Path(self._tmp.name)
        self.tex_path = self.out / "cv-es-software-developer-vacante.tex"
        self.proposal_path = self.out / "cv-es-software-developer-vacante.proposal.json"

    def proposal(self) -> dict:
        return json.loads(self.proposal_path.read_text(encoding="utf-8"))

    def test_load_env_reads_project_root_dotenv(self) -> None:
        env_path = ROOT / ".env"
        backup = env_path.read_text(encoding="utf-8") if env_path.exists() else None
        cwd = os.getcwd()
        try:
            with mock.patch.dict(os.environ):
                os.environ.pop("GROQ_API_KEY", None)
                env_path.write_text("GROQ_API_KEY=test-key-from-root\n", encoding="utf-8")
                os.chdir(ROOT / "tests")
                load_env()
                self.assertEqual(os.getenv("GROQ_API_KEY"), "test-key-from-root")
        finally:
            os.chdir(cwd)
            if backup is None:
                env_path.unlink(missing_ok=True)
            else:
                env_path.write_text(backup, encoding="utf-8")

    def test_local_adaptation_uses_skills_mentioned_in_the_job(self) -> None:
        # Sin clave de Groq: adaptación local y sin preguntar nada.
        with mock.patch.dict(os.environ, KEY), mock.patch.object(generate_cv, "load_env"), \
                mock.patch.object(generate_cv, "adapt_with_groq") as groq, \
                contextlib.redirect_stdout(io.StringIO()):
            os.environ.pop("GROQ_API_KEY")
            code = generate_cv.main([str(EXAMPLE), "--variant", VARIANT, "--job-description", JOB,
                                     "--out", str(self.out)])
        self.assertEqual(code, 0)
        groq.assert_not_called()
        proposal = self.proposal()
        self.assertFalse(proposal["fallback"])
        self.assertEqual(proposal["source"], "local")
        # «Backend & datos» (PostgreSQL) y «Herramientas» (Docker) pasan al frente; empatan y conservan su orden.
        self.assertEqual(proposal["changes"]["skills"][:2], ["Backend & datos", "Herramientas"])
        self.assertIn("Docker", proposal["changes"]["summary"]["after"])
        self.assertIn("PostgreSQL", proposal["changes"]["summary"]["after"])
        tex = self.tex_path.read_text(encoding="utf-8")
        self.assertIn("Experiencia relacionada con la vacante", tex)
        self.assertLess(tex.index("Herramientas"), tex.index("Frontend:"))

    def test_groq_failure_marks_fallback_only_in_proposal_and_console(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq", side_effect=RuntimeError("sin red")):
            code, _, stderr = run_main(self.out, "--yes")
        self.assertEqual(code, 0)
        proposal = self.proposal()
        self.assertTrue(proposal["fallback"])
        self.assertIn("sin red", proposal["fallback_reason"])
        self.assertIn("FALLBACK", stderr)
        tex = self.tex_path.read_text(encoding="utf-8")
        for marker in ("FALLBACK", "Revisar", "Review"):
            self.assertNotIn(marker, tex)

    def test_groq_result_is_applied_and_notes_stay_out_of_the_tex(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq", return_value=GROQ_RESULT):
            code, _, _ = run_main(self.out, "--yes")
        self.assertEqual(code, 0)
        proposal = self.proposal()
        self.assertFalse(proposal["fallback"])
        self.assertEqual(proposal["source"], "groq")
        self.assertIn("Reordené por la vacante.", proposal["review_notes"])
        tex = self.tex_path.read_text(encoding="utf-8")
        self.assertIn("Resumen de IA para la vacante.", tex)
        self.assertNotIn("Reordené", tex)
        self.assertLess(tex.index("Nodo Comercio"), tex.index("Freelance"))

    def test_answering_no_does_not_call_groq(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq") as groq:
            code, stdout, _ = run_main(self.out, interactive=True, answer="n")
        self.assertEqual(code, 0)
        groq.assert_not_called()
        self.assertIn("servicio de terceros", stdout)
        self.assertEqual(self.proposal()["source"], "local")

    def test_answering_s_sends_to_groq(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq", return_value=GROQ_RESULT) as groq:
            run_main(self.out, interactive=True, answer="s")
        groq.assert_called_once()

    def test_non_interactive_without_yes_does_not_call_groq(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq") as groq:
            code, stdout, _ = run_main(self.out, interactive=False)
        self.assertEqual(code, 0)
        groq.assert_not_called()
        self.assertIn("no se envía nada a Groq", stdout)
        self.assertEqual(self.proposal()["source"], "local")

    def test_payload_sent_to_groq_has_no_phone_or_email(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq", return_value=GROQ_RESULT) as groq:
            run_main(self.out, "--yes")
        sent = json.dumps(groq.call_args.args[0], ensure_ascii=False)
        self.assertNotIn(PHONE, sent)
        self.assertNotIn(EMAIL, sent)
        self.assertNotIn("Alex Rivera", sent)
        self.assertIn("Freelance", sent)  # sí viaja el contenido que la IA necesita

    def test_groq_text_is_escaped_for_latex(self) -> None:
        result = {**GROQ_RESULT, "summary": "Experta en R&D con 100% de foco en #1_calidad y {llaves}."}
        with mock.patch.object(generate_cv, "adapt_with_groq", return_value=result):
            run_main(self.out, "--yes")
        tex = self.tex_path.read_text(encoding="utf-8")
        self.assertIn(r"R\&D con 100\% de foco en \#1\_calidad y \{llaves\}.", tex)
        self.assertNotIn("R&D", tex)

    def test_without_job_it_only_renders_the_variants(self) -> None:
        with mock.patch.object(generate_cv, "adapt_with_groq") as groq, contextlib.redirect_stdout(io.StringIO()):
            code = generate_cv.main([str(EXAMPLE), "--out", str(self.out)])
        self.assertEqual(code, 0)
        groq.assert_not_called()
        self.assertEqual(len(list(self.out.glob("cv-*.tex"))), 3)
        self.assertFalse(self.proposal_path.exists())

    def test_unknown_variant_fails_in_spanish(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = generate_cv.main([str(EXAMPLE), "--variant", "fr/nada", "--job-description", JOB,
                                     "--out", str(self.out)])
        self.assertEqual(code, 1)
        self.assertIn("no existe en cv.json", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "ats_check.py"
SPEC = importlib.util.spec_from_file_location("ats_check", SCRIPT_PATH)
assert SPEC is not None
ats_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ats_check)


class AtsCheckTests(unittest.TestCase):
    def test_normalize_removes_accents_and_case(self) -> None:
        self.assertEqual(ats_check.normalize("Análisis"), "analisis")

    def test_normalize_two_words(self) -> None:
        self.assertEqual(ats_check.normalize("Análisis de Datos"), "analisis de datos")

    def test_two_word_keyword_does_not_match_partial(self) -> None:
        result = ats_check.check_text("React", ["React Native"])
        self.assertIn("React Native", result["missing_keywords"])

    def test_sql_not_substring_of_postgresql(self) -> None:
        result = ats_check.check_text("Uso PostgreSQL y Google", ["SQL", "Go"])
        self.assertIn("SQL", result["missing_keywords"])
        self.assertIn("Go", result["missing_keywords"])

    def test_nextjs_matches(self) -> None:
        result = ats_check.check_text("uso Next.js y React", ["Next.js"])
        self.assertIn("Next.js", result["found_keywords"])

    def test_csharp_matches(self) -> None:
        result = ats_check.check_text("C# y .NET", ["C#"])
        self.assertIn("C#", result["found_keywords"])

    def test_short_text_is_not_ok(self) -> None:
        result = ats_check.check_text("texto corto", [])
        self.assertFalse(result["ok"])

    def test_missing_pdftotext_returns_code_2(self) -> None:
        with patch("scripts.ats_check.shutil.which", return_value=None):
            tmp = ROOT / "tests" / "_dummy.pdf"
            tmp.write_bytes(b"%PDF-1.4\n")
            try:
                code = ats_check.main([str(tmp)])
            finally:
                tmp.unlink(missing_ok=True)
            self.assertEqual(code, 2)


    def test_extract_text_decodes_utf8_bytes(self) -> None:
        from unittest.mock import MagicMock

        fake = MagicMock()
        fake.returncode = 0
        fake.stdout = "Análisis de Datos".encode("utf-8")
        fake.stderr = b""
        with patch("scripts.ats_check.shutil.which", return_value="/usr/bin/pdftotext"):
            with patch("scripts.ats_check.subprocess.run", return_value=fake) as run:
                text = ats_check._extract_text(ROOT / "tests" / "_dummy.pdf")
        self.assertEqual(text, "Análisis de Datos")
        self.assertIn("-enc", run.call_args.args[0])
        self.assertIn("UTF-8", run.call_args.args[0])

SECTIONS = ["Perfil", "Experiencia", "Habilidades", "Educación"]
BODY = "relleno " * 40


def cv_text(*titles: str) -> str:
    return "\n".join(f"{title}\n{BODY}" for title in titles)


class SectionOrderTests(unittest.TestCase):
    def test_sections_in_order_are_ok(self) -> None:
        result = ats_check.check_text(cv_text(*SECTIONS), [], SECTIONS)
        self.assertTrue(result["order_ok"])
        self.assertTrue(result["ok"])

    def test_sections_out_of_order_fail(self) -> None:
        text = cv_text("Perfil", "Habilidades", "Experiencia", "Educación")
        result = ats_check.check_text(text, [], SECTIONS)
        self.assertFalse(result["order_ok"])
        self.assertFalse(result["ok"])

    def test_missing_section_title_fails(self) -> None:
        result = ats_check.check_text(cv_text("Perfil", "Experiencia", "Habilidades"), [], SECTIONS)
        self.assertFalse(result["order_ok"])
        self.assertEqual(result["missing_sections"], ["Educación"])

    def test_order_is_not_checked_without_sections(self) -> None:
        result = ats_check.check_text(BODY, [])
        self.assertTrue(result["order_ok"])

    def test_titles_come_from_lang_file(self) -> None:
        self.assertEqual(ats_check.section_titles("es"), SECTIONS)
        self.assertEqual(ats_check.section_titles("en")[0], "Profile")


if __name__ == "__main__":
    unittest.main()

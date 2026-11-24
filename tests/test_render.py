import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.render import escape, render_person, render_variant
from test_cv_model import minimal_cv

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "content" / "example"


class EscapeTests(unittest.TestCase):
    def test_each_special_character(self) -> None:
        expected = {
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
        for char, tex in expected.items():
            with self.subTest(char=char):
                self.assertEqual(escape(f"a{char}b"), f"a{tex}b")

    def test_lone_backslash_has_no_extra_braces(self) -> None:
        self.assertEqual(escape("\\"), r"\textbackslash{}")

    def test_escape_is_a_single_pass(self) -> None:
        self.assertEqual(escape("\\{}"), r"\textbackslash{}\{\}")

    def test_dashes_and_accents_stay_as_is(self) -> None:
        self.assertEqual(escape("Diseño — código"), "Diseño — código")


class RenderVariantTests(unittest.TestCase):
    def test_email_with_underscore_inside_href(self) -> None:
        cv = minimal_cv()
        cv["person"]["email"] = "alex_rivera@example.com"
        tex = render_variant(cv, "es", "software-developer")
        self.assertIn(r"\href{mailto:alex_rivera@example.com}{alex\_rivera@example.com}", tex)

    def test_url_escapes_only_percent_and_hash(self) -> None:
        cv = minimal_cv()
        cv["more"]["url"] = "https://example.com/a_b?x=1%20#top"
        tex = render_variant(cv, "es", "software-developer")
        self.assertIn(r"\href{https://example.com/a_b?x=1\%20\#top}{example.com}", tex)

    def test_null_end_is_present_label(self) -> None:
        tex = render_variant(minimal_cv(), "es", "software-developer")
        self.assertIn(r"\ckEntry{Desarrolladora}{2023 -- \LblPresent}{Freelance}{}", tex)

    def test_education_without_start_shows_only_end(self) -> None:
        tex = render_variant(minimal_cv(), "es", "software-developer")
        self.assertIn(r"\ckEntry{Técnica}{2021}{Instituto}{}", tex)

    def test_preamble_inputs_lang_and_style_from_repo_root(self) -> None:
        tex = render_variant(minimal_cv(), "es", "software-developer")
        self.assertIn(r"\input{lang/es.tex}", tex)
        self.assertIn(r"\input{styles/modern.tex}", tex)


class RenderExampleTests(unittest.TestCase):
    def test_example_renders_one_file_per_variant_with_keywords(self) -> None:
        cv = json.loads((EXAMPLE / "cv.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as out:
            written = render_person(EXAMPLE, out)
            self.assertEqual(len(written), 3)
            for variant in cv["variants"]:
                lang, profile = variant["lang"], variant["profile"]
                path = Path(out) / f"cv-{lang}-{profile}.tex"
                self.assertIn(path, written)
                tex = path.read_text(encoding="utf-8")
                keywords = cv["profiles"][profile]["keywords"][lang]
                with self.subTest(variant=path.name):
                    self.assertIn(f"pdfkeywords={{{', '.join(keywords)}}}", tex)
                    # Cada keyword debe estar también en el cuerpo, que es lo que lee un ATS.
                    body = tex.split(r"\begin{document}", 1)[1]
                    for keyword in keywords:
                        self.assertIn(keyword, body)


class NoPersonalDataTests(unittest.TestCase):
    # Partidos en dos para que este archivo no se detecte a sí mismo.
    FORBIDDEN = ("@" + "gmail", "+57" + " 3")

    def test_versioned_files_have_no_personal_data(self) -> None:
        try:
            listed = subprocess.run(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                cwd=ROOT, capture_output=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("git no disponible")
        for name in filter(None, listed.decode("utf-8").split("\0")):
            path = ROOT / name
            if not path.is_file():
                continue
            content = path.read_bytes()
            for needle in self.FORBIDDEN:
                with self.subTest(file=name, needle=needle):
                    self.assertFalse(needle.encode("utf-8") in content, f"{name} contiene {needle!r}")


if __name__ == "__main__":
    unittest.main()

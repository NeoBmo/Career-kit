import copy
import unittest
from typing import Any

from scripts.cv_model import CvError, validate


def minimal_cv() -> dict[str, Any]:
    """cv.json mínimo y válido con una variante en español."""
    return {
        "person": {
            "name": "Alex Rivera",
            "location": {"es": "Medellín, Colombia", "en": "Medellín, Colombia"},
            "phone": "+00 000 000 0000",
            "email": "alex@example.com",
        },
        "more": {"label": "example.com", "url": "https://example.com"},
        "profiles": {
            "software-developer": {
                "title": {"es": "Desarrolladora de Software", "en": "Software Developer"},
                "summary": {"es": "Resumen.", "en": "Summary."},
                "keywords": {"es": ["React", "SQL"], "en": ["React", "SQL"]},
            }
        },
        "experience": [
            {"role": {"es": "Desarrolladora", "en": "Developer"}, "organization": "Freelance",
             "start": "2023", "end": None, "highlights": {"es": ["Logro."], "en": ["Win."]}},
        ],
        "skills": [{"label": {"es": "Frontend", "en": "Frontend"}, "items": {"es": "React", "en": "React"}}],
        "education": [
            {"title": {"es": "Técnica", "en": "Technician"}, "organization": "Instituto",
             "start": None, "end": "2021", "details": {"es": "Detalles.", "en": "Details."}},
        ],
        "variants": [{"lang": "es", "profile": "software-developer"}],
    }


class CvModelTests(unittest.TestCase):
    def assert_error(self, data: dict[str, Any], path: str) -> CvError:
        with self.assertRaises(CvError) as ctx:
            validate(data)
        self.assertTrue(any(e.startswith(f"{path}:") for e in ctx.exception.errors),
                        f"no hay error en {path}: {ctx.exception.errors}")
        return ctx.exception

    def test_minimal_cv_is_valid(self) -> None:
        validate(minimal_cv())

    def test_error_reports_exact_field_path(self) -> None:
        data = minimal_cv()
        data["experience"].append(copy.deepcopy(data["experience"][0]))
        data["experience"].append(copy.deepcopy(data["experience"][0]))
        data["experience"][2]["highlights"]["en"] = "not a list"
        self.assert_error(data, "experience[2].highlights.en")

    def test_missing_field_reports_its_path(self) -> None:
        data = minimal_cv()
        del data["person"]["email"]
        self.assert_error(data, "person.email")

    def test_text_missing_in_variant_language(self) -> None:
        data = minimal_cv()
        data["variants"].append({"lang": "en", "profile": "software-developer"})
        del data["education"][0]["details"]["en"]
        error = self.assert_error(data, "education[0].details.en")
        self.assertIn("en/software-developer", str(error))

    def test_unused_language_is_not_required(self) -> None:
        data = minimal_cv()
        del data["profiles"]["software-developer"]["summary"]["en"]
        validate(data)

    def test_variant_with_unknown_profile(self) -> None:
        data = minimal_cv()
        data["variants"][0]["profile"] = "react-developer"
        self.assert_error(data, "variants[0].profile")

    def test_end_must_be_string_or_null(self) -> None:
        data = minimal_cv()
        data["experience"][0]["end"] = 2024
        self.assert_error(data, "experience[0].end")

    def test_experience_needs_at_least_one_highlight(self) -> None:
        data = minimal_cv()
        data["experience"][0]["highlights"]["es"] = []
        self.assert_error(data, "experience[0].highlights.es")

    def test_more_is_optional(self) -> None:
        data = minimal_cv()
        del data["more"]
        validate(data)

    def test_more_if_present_is_validated(self) -> None:
        data = minimal_cv()
        del data["more"]["url"]
        self.assert_error(data, "more.url")

    def test_empty_sections_are_valid(self) -> None:
        data = minimal_cv()
        data["experience"], data["education"], data["skills"] = [], [], []
        validate(data)

    def test_path_traversal_in_profile_is_rejected(self) -> None:
        data = minimal_cv()
        data["profiles"]["x/../../y"] = data["profiles"].pop("software-developer")
        data["variants"][0]["profile"] = "x/../../y"
        self.assert_error(data, "profiles.x/../../y")
        self.assert_error(data, "variants[0].profile")

    def test_variant_lang_must_be_a_slug(self) -> None:
        data = minimal_cv()
        data["variants"][0]["lang"] = "../es"
        error = self.assert_error(data, "variants[0].lang")
        self.assertIn("minúsculas", str(error))

    def test_slug_rejects_uppercase_and_trailing_newline(self) -> None:
        for bad in ("Es", "es\n", "e s", ""):
            with self.subTest(bad=bad):
                data = minimal_cv()
                data["variants"][0]["lang"] = bad
                with self.assertRaises(CvError):
                    validate(data)


if __name__ == "__main__":
    unittest.main()

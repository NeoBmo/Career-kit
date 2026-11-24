import json
import unittest
from unittest import mock

from scripts import groq_client
from scripts.groq_client import GroqResponseError, _validate_structure

PAYLOAD = {"experiences": [{"index": 0}, {"index": 1}], "skills": [{"index": 0}]}
GOOD = {"summary": "S", "experience_order": [1, 0], "skills_order": [0], "notes": "ok"}


def groq_reply(content: str) -> dict:
    return {"choices": [{"message": {"content": content}}]}


class ValidateStructureTests(unittest.TestCase):
    def test_validate_ok(self) -> None:
        ok, msg = _validate_structure(GOOD, PAYLOAD)
        self.assertTrue(ok, msg)

    def test_rejects_bad_responses(self) -> None:
        bad = {
            "falta una clave": {k: v for k, v in GOOD.items() if k != "notes"},
            "resumen vacío": {**GOOD, "summary": "  "},
            "resumen NO_INFO": {**GOOD, "summary": "NO_INFO"},
            "índice fuera de rango": {**GOOD, "experience_order": [0, 5]},
            "índice repetido": {**GOOD, "skills_order": [0, 0]},
            "lista vacía": {**GOOD, "experience_order": []},
            "booleano como índice": {**GOOD, "skills_order": [True]},
        }
        for name, obj in bad.items():
            with self.subTest(name):
                self.assertFalse(_validate_structure(obj, PAYLOAD)[0])


class AdaptWithGroqTests(unittest.TestCase):
    def test_returns_parsed_response(self) -> None:
        with mock.patch.object(groq_client, "call_groq_raw", return_value=groq_reply(json.dumps(GOOD))):
            self.assertEqual(groq_client.adapt_with_groq(PAYLOAD, "vacante"), GOOD)

    def test_extracts_json_wrapped_in_text(self) -> None:
        content = "Aquí está:\n" + json.dumps(GOOD) + "\nListo."
        with mock.patch.object(groq_client, "call_groq_raw", return_value=groq_reply(content)):
            self.assertEqual(groq_client.adapt_with_groq(PAYLOAD, "vacante"), GOOD)

    def test_raises_on_unusable_response(self) -> None:
        for content in ("", "no es json", json.dumps({**GOOD, "experience_order": [9]})):
            with self.subTest(content=content):
                with mock.patch.object(groq_client, "call_groq_raw", return_value=groq_reply(content)):
                    with self.assertRaises(GroqResponseError):
                        groq_client.adapt_with_groq(PAYLOAD, "vacante")


if __name__ == "__main__":
    unittest.main()

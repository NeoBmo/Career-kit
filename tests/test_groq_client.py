import unittest

from scripts.groq_client import _validate_structure


class GroqClientTests(unittest.TestCase):
    def test_validate_ok(self) -> None:
        sample = {
            "objective": "O",
            "summary": "S",
            "relevant_skills": ["A"],
            "relevant_experiences": [{
                "role": "r",
                "organization": "o",
                "dates": "d",
                "details": ["x"],
                "relevance_score": 1
            }],
            "notes": "ok"
        }
        ok, msg = _validate_structure(sample)
        self.assertTrue(ok, msg)


if __name__ == "__main__":
    unittest.main()

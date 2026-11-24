import re
import unittest
from pathlib import Path

CI = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


class CiWorkflowTests(unittest.TestCase):
    def test_every_action_is_pinned_with_a_version_comment(self) -> None:
        uses = re.findall(r"^\s*uses: (\S+)(.*)$", CI, flags=re.M)
        self.assertTrue(uses)
        for ref, rest in uses:
            with self.subTest(ref=ref):
                self.assertRegex(ref, r"@[0-9a-f]{40}$")
                self.assertRegex(rest, r"# v\d+\.\d+\.\d+")

    def test_checkout_does_not_persist_credentials(self) -> None:
        checkouts = CI.count("uses: actions/checkout@")
        self.assertEqual(checkouts, 3)
        self.assertEqual(len(re.findall(r"uses: actions/checkout@.*\n\s+with:\n\s+persist-credentials: false", CI)),
                         checkouts)

    def test_public_copy_job_warns_in_spanish_without_injection(self) -> None:
        self.assertIn("if: github.repository != 'NeoBmo/Career-kit'", CI)
        self.assertIn("REPO_PRIVATE: ${{ github.event.repository.private }}", CI)
        self.assertIn("Tu copia es PÚBLICA", CI)
        self.assertIn("Settings → General → Danger Zone → Change visibility", CI)
        # Ninguna expresión ${{ }} dentro de un bloque run: ni en su línea.
        for block in re.findall(r"^\s*run: .*(?:\n(?:\s{10,}.*|))*", CI, flags=re.M):
            self.assertNotIn("${{", block)


if __name__ == "__main__":
    unittest.main()

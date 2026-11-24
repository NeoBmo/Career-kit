import unittest
from scripts.privacy_check import check_text


class PrivacyCheckTests(unittest.TestCase):
    def test_clean_text_passes(self) -> None:
        text = "Contacto: alex@example.com\nTel: +00 000 000 0000"
        self.assertEqual(check_text(text), [])

    def test_real_email_detected(self) -> None:
        text = "Escríbeme a luis@" + "bar.com"
        violations = check_text(text)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["line"], 1)
        self.assertEqual(violations[0]["type"], "email")

    def test_noreply_allowed(self) -> None:
        text = "noreply@github.com"
        self.assertEqual(len(check_text(text)), 0)

    def test_example_domain_allowed(self) -> None:
        text = "alex@example.com"
        self.assertEqual(len(check_text(text)), 0)

    def test_real_phone_detected(self) -> None:
        text = "Tel: +1 234 " + "567 8901"
        violations = check_text(text)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["type"], "phone")

    def test_placeholder_phone_allowed(self) -> None:
        text = "Tel: +00 000 000 0000"
        self.assertEqual(len(check_text(text)), 0)

    def test_line_number_reported(self) -> None:
        text = "línea ok\nsecreto: foo@bar.com"
        violations = check_text(text)
        self.assertEqual(violations[0]["line"], 2)

    def test_ten_digit_phone_detected(self) -> None:
        text = "12345" + "67890"
        self.assertEqual(len(check_text(text)), 1)


if __name__ == "__main__":
    unittest.main()

import unittest

from src.privacy_engine import PrivacyEngine


class PrivacyBoundaryRegressionTests(unittest.TestCase):
    def test_sensitive_values_are_removed_from_agent_payload(self):
        raw = {
            "schema_version": "1.0",
            "page_state_id": "PS_privacy_001",
            "captured_at": "2026-09-29T12:00:00Z",
            "url": "https://example.test/profile",
            "title": "Account",
            "visible_text": "Contact alice@example.com",
            "elements": [
                {
                    "element_id": "EL_001",
                    "role": "text",
                    "label": "alice@example.com",
                    "visible": True,
                    "enabled": True,
                }
            ],
        }

        engine = PrivacyEngine()
        sanitized = engine.sanitize(raw)
        payload = str(sanitized)

        self.assertNotIn("alice@example.com", payload)
        self.assertTrue(sanitized["privacy_summary"]["verification_passed"])
        self.assertGreater(sanitized["privacy_summary"]["redaction_count"], 0)

    def test_local_mapping_is_not_exposed_in_sanitized_state(self):
        raw = {
            "schema_version": "1.0",
            "page_state_id": "PS_privacy_002",
            "captured_at": "2026-09-29T12:00:00Z",
            "url": "https://example.test",
            "title": "Login",
            "visible_text": "Password: SuperSecret42",
            "elements": [],
        }

        engine = PrivacyEngine()
        sanitized = engine.sanitize(raw)
        mapping = engine.get_local_mapping()

        self.assertTrue(mapping)
        self.assertNotIn("local_mapping", sanitized)
        self.assertNotIn("SuperSecret42", str(sanitized))
        self.assertTrue(sanitized["privacy_summary"]["verification_passed"])

    def test_clear_session_removes_restoration_state(self):
        engine = PrivacyEngine()
        engine.sanitize({
            "schema_version": "1.0",
            "page_state_id": "PS_privacy_003",
            "captured_at": "2026-09-29T12:00:00Z",
            "url": "https://example.test",
            "title": "Profile",
            "visible_text": "alice@example.com",
            "elements": [],
        })

        self.assertTrue(engine.get_local_mapping())
        engine.clear_session()

        self.assertEqual(engine.get_local_mapping(), {})
        self.assertEqual(
            engine.get_privacy_stats()["status"],
            "no_sanitization_performed",
        )


if __name__ == "__main__":
    unittest.main()

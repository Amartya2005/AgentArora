import unittest
from src.privacy_engine import PrivacyEngine

class PrivacyStatsContractTests(unittest.TestCase):
    def test_initial_stats_are_empty_and_stable(self):
        stats=PrivacyEngine().get_privacy_stats()
        self.assertEqual(stats["status"],"no_sanitization_performed")
        self.assertEqual(stats["redaction_count"],0)
        self.assertEqual(stats["categories"],[])
        self.assertEqual(stats["placeholder_count"],0)
    def test_clear_session_resets_last_state(self):
        engine=PrivacyEngine(); engine.clear_session()
        self.assertEqual(engine.get_privacy_stats()["status"],"no_sanitization_performed")

if __name__ == "__main__": unittest.main()

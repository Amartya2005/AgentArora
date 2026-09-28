import unittest
from src.privacy_engine import PrivacyEngine

class PrivacyStatsAfterClearTests(unittest.TestCase):
    def test_clear_session_removes_previous_sanitization_state(self):
        engine=PrivacyEngine(); engine.clear_session()
        stats=engine.get_privacy_stats()
        self.assertEqual(stats["placeholder_count"],0)
        self.assertEqual(stats["categories"],[])
        self.assertFalse(stats.get("verification_passed",False))

if __name__ == "__main__": unittest.main()

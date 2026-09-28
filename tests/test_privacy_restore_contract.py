import unittest
from src.privacy_engine import PrivacyEngine

class PrivacyRestoreContractTests(unittest.TestCase):
    def test_unknown_placeholder_is_left_unchanged(self):
        engine=PrivacyEngine()
        self.assertEqual(engine.restore_value("[EMAIL_99]"),None)
        self.assertEqual(engine.restore_text("hello [EMAIL_99]"),"hello [EMAIL_99]")
    def test_mapping_is_returned_as_a_copy(self):
        engine=PrivacyEngine()
        mapping=engine.get_local_mapping(); mapping["[EMAIL_01]"]="leak"
        self.assertNotIn("[EMAIL_01]",engine.get_local_mapping())

if __name__ == "__main__": unittest.main()

import unittest
from src.privacy_engine import PrivacyEngine

class PrivacyMappingCopyTests(unittest.TestCase):
    def test_each_mapping_read_is_independent(self):
        engine=PrivacyEngine()
        first=engine.get_local_mapping(); second=engine.get_local_mapping()
        self.assertIsNot(first,second)
        first.clear()
        self.assertEqual(engine.get_local_mapping(),{})

if __name__ == "__main__": unittest.main()

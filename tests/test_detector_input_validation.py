import unittest
from src.detector import evaluate_item

class DetectorInputValidationTests(unittest.TestCase):
    def test_empty_values_are_not_detected_as_sensitive(self):
        for category in ("email","phone","person","address"):
            self.assertFalse(evaluate_item(category,""))
    def test_whitespace_values_are_safe(self):
        self.assertFalse(evaluate_item("email","   "))

if __name__ == "__main__": unittest.main()

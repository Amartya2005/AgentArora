import unittest
from src.detector import evaluate_item

class DetectorWhitespaceTests(unittest.TestCase):
    def test_email_whitespace_is_not_a_match(self):
        self.assertFalse(evaluate_item("email"," \t\n "))
    def test_phone_whitespace_is_not_a_match(self):
        self.assertFalse(evaluate_item("phone","   "))

if __name__ == "__main__": unittest.main()

import unittest
from agent.risk_policy import classify_action

class RiskPolicyKeyboardTests(unittest.TestCase):
    def test_high_risk_keyboard_action_requires_confirmation(self):
        risk, confirm = classify_action({"action_type":"PRESS_KEY","risk_level":"HIGH"},None)
        self.assertEqual(risk,"HIGH"); self.assertTrue(confirm)
    def test_low_risk_scroll_stays_low(self):
        risk, confirm = classify_action({"action_type":"SCROLL","risk_level":"LOW"},None)
        self.assertEqual(risk,"LOW"); self.assertFalse(confirm)

if __name__ == "__main__": unittest.main()

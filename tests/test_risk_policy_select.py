import unittest
from agent.risk_policy import classify_action

class RiskPolicySelectTests(unittest.TestCase):
    def test_select_sensitive_field_is_high_risk(self):
        risk, confirm = classify_action({"action_type":"SELECT"},{"role":"textbox","sensitivity":"PASSWORD"})
        self.assertEqual(risk,"HIGH"); self.assertTrue(confirm)
    def test_medium_risk_remains_medium_without_sensitive_target(self):
        risk, confirm = classify_action({"action_type":"CLICK","risk_level":"MEDIUM"},{"label":"Continue"})
        self.assertEqual(risk,"MEDIUM"); self.assertFalse(confirm)

if __name__ == "__main__": unittest.main()

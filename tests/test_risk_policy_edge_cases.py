import unittest
from agent.risk_policy import classify_action

class RiskPolicyEdgeCaseTests(unittest.TestCase):
    def test_whitespace_and_case_in_submit_label(self):
        risk, confirm = classify_action({"action_type":"CLICK"},{"label":"  PAY  "})
        self.assertEqual(risk,"HIGH"); self.assertTrue(confirm)

    def test_unknown_requested_risk_defaults_to_low(self):
        risk, confirm = classify_action({"action_type":"CLICK","risk_level":"critical"},{"label":"Continue"})
        self.assertEqual(risk,"LOW"); self.assertFalse(confirm)

    def test_sensitive_role_overrides_low_risk(self):
        risk, confirm = classify_action({"action_type":"TYPE","risk_level":"LOW"},{"role":"password","sensitivity":"NONE"})
        self.assertEqual(risk,"HIGH"); self.assertTrue(confirm)

if __name__ == "__main__": unittest.main()

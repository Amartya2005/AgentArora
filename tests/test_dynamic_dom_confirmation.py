import unittest
from agent.dynamic_dom import DynamicDOMOrchestrator

class DynamicDOMConfirmationTests(unittest.TestCase):
    def test_confirmation_gate_blocks_retry_even_when_low_risk(self):
        action={"risk_level":"LOW","requires_user_confirmation":True,"target_element_id":"EL_old"}
        result={"status":"STALE_ELEMENT"}
        d=DynamicDOMOrchestrator().handle_action_result(result,action,0)
        self.assertFalse(d.allowed)
        self.assertEqual(d.result["error"]["code"],"POLICY_BLOCKED")
        self.assertFalse(d.result["error"]["retryable"])

if __name__ == "__main__": unittest.main()

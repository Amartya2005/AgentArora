import unittest
from agent.dynamic_dom import DynamicDOMOrchestrator

class DynamicDOMRecoveryLimitTests(unittest.TestCase):
    def test_custom_limit_is_respected(self):
        orch=DynamicDOMOrchestrator(max_stale_recoveries=3)
        action={"risk_level":"LOW"}; result={"status":"STALE_ELEMENT"}
        self.assertTrue(orch.handle_action_result(result,action,2).allowed)
        self.assertFalse(orch.handle_action_result(result,action,3).allowed)

if __name__ == "__main__": unittest.main()

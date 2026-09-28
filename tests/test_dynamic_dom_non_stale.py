import unittest
from agent.dynamic_dom import DynamicDOMOrchestrator

class DynamicDOMNonStaleTests(unittest.TestCase):
    def test_success_result_is_returned_unchanged(self):
        result={"status":"SUCCESS","action_id":"ACT_1"}
        decision=DynamicDOMOrchestrator().handle_action_result(result,{"risk_level":"LOW"},0)
        self.assertEqual(decision.result,result)
        self.assertFalse(decision.needs_fresh_page_state)

if __name__ == "__main__": unittest.main()

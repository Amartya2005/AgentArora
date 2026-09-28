import unittest
from agent.dynamic_dom import DynamicDOMOrchestrator

class DynamicDOMRefreshContractTests(unittest.TestCase):
    def test_missing_fresh_state_id_stops_replan(self):
        orch=DynamicDOMOrchestrator()
        decision=orch.replan_after_refresh(
            agent=type("A",(),{"create_plan":lambda *a,**k: None})(),
            user_task={"task_id":"T"}, action_result={"status":"STALE_ELEMENT"},
            original_action={"risk_level":"LOW"}, fresh_sanitized_page_state={}, stale_recoveries=0)
        self.assertEqual(decision.action_result["status"],"BLOCKED_BY_POLICY")
        self.assertFalse(decision.action_result["error"]["retryable"])

if __name__ == "__main__": unittest.main()

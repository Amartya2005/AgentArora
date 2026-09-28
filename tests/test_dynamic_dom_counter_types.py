import unittest
from agent.dynamic_dom import DynamicDOMOrchestrator

class DynamicDOMCounterTypeTests(unittest.TestCase):
    def setUp(self): self.orch=DynamicDOMOrchestrator()
    def result(self): return {"status":"STALE_ELEMENT","error":{"code":"STALE_ELEMENT"}}
    def action(self): return {"risk_level":"LOW","requires_user_confirmation":False}
    def test_boolean_counter_is_rejected(self):
        d=self.orch.handle_action_result(self.result(),self.action(),True)
        self.assertFalse(d.allowed); self.assertEqual(d.result["status"],"BLOCKED_BY_POLICY")
    def test_negative_counter_is_rejected(self):
        d=self.orch.handle_action_result(self.result(),self.action(),-1)
        self.assertFalse(d.allowed); self.assertEqual(d.result["status"],"BLOCKED_BY_POLICY")
    def test_non_stale_result_is_passthrough(self):
        r={"status":"SUCCESS","value":1}; d=self.orch.handle_action_result(r,self.action(),0)
        self.assertFalse(d.allowed); self.assertEqual(d.result,r)

if __name__ == "__main__": unittest.main()

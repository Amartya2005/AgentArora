import unittest
from collections import deque

from agent import Agent, BrowserAgentRuntime
from src.privacy_engine import PrivacyEngine


class FakeBridge:
    def __init__(self, page_states):
        self.page_states = deque(page_states)

    def wait_for_page_state(self, timeout=30.0):
        if not self.page_states:
            raise TimeoutError("no test PageState available")
        return self.page_states.popleft()


class FakeTransport:
    def __init__(self, page_states, action_results):
        self.bridge = FakeBridge(page_states)
        self.action_results = deque(action_results)
        self.started = False
        self.plans = []

    def start(self):
        self.started = True

    def execute_action_plan(self, plan, timeout=30.0):
        self.plans.append(plan)
        if not self.action_results:
            raise AssertionError("No fake ActionResult configured")
        return self.action_results.popleft()


def page_state(state_id, element_id, visible_text):
    return {
        "schema_version": "1.0",
        "page_state_id": state_id,
        "captured_at": "2026-09-17T05:00:00Z",
        "url": "http://localhost:8080/test-page/index.html",
        "title": "Test Page",
        "visible_text": visible_text,
        "elements": [
            {
                "element_id": element_id,
                "role": "button",
                "type": "button",
                "label": "Continue",
                "text": "Continue",
                "visible": True,
                "enabled": True,
                "bounds": {
                    "x": 10,
                    "y": 10,
                    "width": 100,
                    "height": 40,
                },
            }
        ],
    }


def action_result(plan, status, needs_fresh=False):
    action = plan["actions"][0]
    return {
        "schema_version": "1.0",
        "action_plan_id": plan["action_plan_id"],
        "action_id": action["action_id"],
        "completed_at": "2026-09-17T05:00:01Z",
        "status": status,
        "observed_change": "Test browser result.",
        "needs_fresh_page_state": needs_fresh,
        **({
            "error": {
                "code": "STALE_ELEMENT",
                "message": "Target was stale.",
                "retryable": True,
            }
        } if status == "STALE_ELEMENT" else {}),
    }


class RecordingAgent:
    def __init__(self):
        self.delegate = Agent()
        self.states = []

    def create_plan(self, user_task, sanitized_page_state):
        self.states.append(sanitized_page_state)
        return self.delegate.create_plan(user_task, sanitized_page_state)


class BrowserRuntimeTests(unittest.TestCase):
    def test_runtime_routes_page_state_through_privacy_and_recovers_stale_target(self):
        raw_email = "student@example.com"
        transport = FakeTransport(
            page_states=[
                page_state("PS_day5_001", "EL_100", f"Welcome {raw_email}"),
                page_state("PS_day5_002", "EL_200", "Reports page"),
            ],
            action_results=[],
        )
        recorder = RecordingAgent()
        runtime = BrowserAgentRuntime(
            transport=transport,
            privacy_engine=PrivacyEngine(),
            agent=recorder,
        )

        runtime_task = {"task_id": "TASK_day5_001", "natural_language_goal": "Open the page."}

        first_plan_holder = {}
        original_execute = transport.execute_action_plan
        calls = {"count": 0}

        def execute(plan, timeout=30.0):
            calls["count"] += 1
            original_execute.plan = plan
            if calls["count"] == 1:
                return [action_result(plan, "STALE_ELEMENT")]
            return [action_result(plan, "SUCCESS")]

        transport.execute_action_plan = execute
        result = runtime.run(runtime_task, page_state_timeout=1.0, action_timeout=1.0)

        self.assertTrue(transport.started)
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.stale_recoveries, 1)
        self.assertEqual(calls["count"], 2)
        self.assertEqual(len(recorder.states), 2)
        self.assertNotIn(raw_email, str(recorder.states[0]))
        self.assertEqual(
            recorder.states[0]["source_page_state_id"],
            "PS_day5_001",
        )
        self.assertEqual(
            recorder.states[1]["source_page_state_id"],
            "PS_day5_002",
        )

    def test_runtime_reports_privacy_failure_instead_of_hiding_it(self):
        invalid_state = {"page_state_id": "PS_bad"}
        transport = FakeTransport(
            page_states=[invalid_state],
            action_results=[],
        )
        runtime = BrowserAgentRuntime(transport=transport)

        result = runtime.run(
            "Open the page.",
            page_state_timeout=1.0,
            action_timeout=1.0,
        )

        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.failure["code"], "PRIVACY_BOUNDARY_FAILURE")
        self.assertIn("required", result.failure["message"])


if __name__ == "__main__":
    unittest.main()

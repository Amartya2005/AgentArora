"""Production Day 5 runtime connecting perception, privacy, reasoning, and actions."""

from __future__ import annotations

import argparse
import uuid
from dataclasses import dataclass
from typing import Any, Mapping

from src.privacy_engine import PrivacyEngine

from .agent import Agent, AgentOutput
from .dynamic_dom import DynamicDOMOrchestrator
from .transport import LocalBrowserTransport


DEFAULT_PAGE_STATE_TIMEOUT = 30.0
DEFAULT_ACTION_TIMEOUT = 30.0


@dataclass(frozen=True)
class RuntimeResult:
    status: str
    action_results: tuple[dict[str, Any], ...] = ()
    failure: dict[str, Any] | None = None
    stale_recoveries: int = 0


class BrowserAgentRuntime:
    """Bounded production coordinator for the Day 5 browser loop.

    Flow:
        Browser PageState -> PrivacyEngine -> Agent -> ActionPlan -> Browser
        ActionResult -> bounded stale recovery when required.

    Raw PageState is consumed locally and is never passed into Agent.create_plan.
    """

    def __init__(
        self,
        transport: LocalBrowserTransport | None = None,
        privacy_engine: PrivacyEngine | None = None,
        agent: Agent | None = None,
        dynamic_dom: DynamicDOMOrchestrator | None = None,
    ) -> None:
        self.transport = transport or LocalBrowserTransport()
        self.privacy_engine = privacy_engine or PrivacyEngine()
        self.agent = agent or Agent()
        self.dynamic_dom = dynamic_dom or DynamicDOMOrchestrator()

    @staticmethod
    def _task_from_input(user_task: str | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(user_task, Mapping):
            task = dict(user_task)
            if not task.get("task_id") or not task.get("natural_language_goal"):
                raise ValueError("user_task mapping requires task_id and natural_language_goal")
            return task

        goal = str(user_task).strip()
        if not goal:
            raise ValueError("user task cannot be empty")
        return {
            "task_id": "TASK_runtime_" + uuid.uuid4().hex[:12],
            "natural_language_goal": goal,
        }

    def run(
        self,
        user_task: str | Mapping[str, Any],
        *,
        page_state_timeout: float = DEFAULT_PAGE_STATE_TIMEOUT,
        action_timeout: float = DEFAULT_ACTION_TIMEOUT,
    ) -> RuntimeResult:
        task = self._task_from_input(user_task)
        stale_recoveries = 0

        self.transport.start()
        try:
            raw_page_state = self.transport.bridge.wait_for_page_state(page_state_timeout)
            return self._run_from_page_state(
                task,
                raw_page_state,
                stale_recoveries=stale_recoveries,
                action_timeout=action_timeout,
            )
        except Exception as exc:
            return RuntimeResult(
                status="FAIL",
                failure={
                    "code": "RUNTIME_FAILURE",
                    "message": str(exc),
                },
                stale_recoveries=stale_recoveries,
            )

    def _sanitize(self, raw_page_state: Mapping[str, Any], stale_recoveries: int) -> tuple[dict[str, Any] | None, RuntimeResult | None]:
        try:
            return self.privacy_engine.sanitize(dict(raw_page_state)), None
        except Exception as exc:
            return None, RuntimeResult(
                status="FAIL",
                failure={
                    "code": "PRIVACY_BOUNDARY_FAILURE",
                    "message": str(exc),
                },
                stale_recoveries=stale_recoveries,
            )

    def _run_from_page_state(
        self,
        task: Mapping[str, Any],
        raw_page_state: Mapping[str, Any],
        *,
        stale_recoveries: int,
        action_timeout: float,
    ) -> RuntimeResult:
        sanitized_page_state, privacy_failure = self._sanitize(raw_page_state, stale_recoveries)
        if privacy_failure:
            return privacy_failure
        assert sanitized_page_state is not None

        output = self.agent.create_plan(task, sanitized_page_state)
        if output.action_result is not None:
            return RuntimeResult(
                status="FAIL",
                action_results=(dict(output.action_result),),
                failure=output.action_result.get("error"),
                stale_recoveries=stale_recoveries,
            )
        if output.action_plan is None:
            return RuntimeResult(
                status="FAIL",
                failure={
                    "code": "NO_ACTION_PLAN",
                    "message": "Agent produced neither an action plan nor a safe failure result.",
                },
                stale_recoveries=stale_recoveries,
            )

        current_plan = output.action_plan
        current_results: list[dict[str, Any]] = []
        current_actions: list[Mapping[str, Any]] = current_plan.get("actions", [])

        while True:
            try:
                current_results = self.transport.execute_action_plan(current_plan, action_timeout)
            except Exception as exc:
                return RuntimeResult(
                    status="FAIL",
                    failure={
                        "code": "BROWSER_TRANSPORT_FAILURE",
                        "message": str(exc),
                    },
                    stale_recoveries=stale_recoveries,
                )

            if not current_results:
                return RuntimeResult(
                    status="FAIL",
                    failure={
                        "code": "EMPTY_ACTION_RESULT",
                        "message": "Browser returned no ActionResult records.",
                    },
                    stale_recoveries=stale_recoveries,
                )

            stale_result = None
            stale_action: Mapping[str, Any] | None = None
            for index, action_result in enumerate(current_results):
                if action_result.get("status") != "SUCCESS":
                    stale_result = action_result
                    stale_action = current_actions[index] if index < len(current_actions) else current_actions[0]
                    break

            if stale_result is None:
                return RuntimeResult(
                    status="SUCCESS",
                    action_results=tuple(dict(item) for item in current_results),
                    stale_recoveries=stale_recoveries,
                )

            decision = self.dynamic_dom.handle_action_result(
                stale_result,
                stale_action,
                stale_recoveries,
            )
            if not decision.allowed:
                failure_result = decision.result or dict(stale_result)
                return RuntimeResult(
                    status="FAIL",
                    action_results=tuple(dict(item) for item in current_results),
                    failure=failure_result.get("error"),
                    stale_recoveries=stale_recoveries,
                )

            stale_recoveries += 1
            try:
                fresh_raw_page_state = self.transport.bridge.wait_for_page_state(DEFAULT_PAGE_STATE_TIMEOUT)
                fresh_sanitized_page_state, privacy_failure = self._sanitize(
                    fresh_raw_page_state,
                    stale_recoveries,
                )
                if privacy_failure:
                    return privacy_failure
                assert fresh_sanitized_page_state is not None

                replanned: AgentOutput = self.dynamic_dom.replan_after_refresh(
                    self.agent,
                    task,
                    stale_result,
                    stale_action,
                    fresh_sanitized_page_state,
                    stale_recoveries,
                )
            except Exception as exc:
                return RuntimeResult(
                    status="FAIL",
                    action_results=tuple(dict(item) for item in current_results),
                    failure={
                        "code": "STALE_RECOVERY_FAILURE",
                        "message": str(exc),
                    },
                    stale_recoveries=stale_recoveries,
                )

            if replanned.action_result is not None:
                return RuntimeResult(
                    status="FAIL",
                    action_results=tuple(dict(item) for item in current_results),
                    failure=replanned.action_result.get("error"),
                    stale_recoveries=stale_recoveries,
                )
            if replanned.action_plan is None:
                return RuntimeResult(
                    status="FAIL",
                    action_results=tuple(dict(item) for item in current_results),
                    failure={
                        "code": "REPLAN_FAILED",
                        "message": "Fresh-state reasoning produced no action plan.",
                    },
                    stale_recoveries=stale_recoveries,
                )

            current_plan = replanned.action_plan
            current_actions = current_plan.get("actions", [])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AgentArora browser-agent runtime.")
    parser.add_argument("task", help="Natural-language task for the browser agent.")
    args = parser.parse_args()

    runtime = BrowserAgentRuntime()
    result = runtime.run(args.task)
    print({
        "status": result.status,
        "action_result_statuses": [item.get("status") for item in result.action_results],
        "failure": result.failure,
        "stale_recoveries": result.stale_recoveries,
    })
    return 0 if result.status == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

# Agent Loop Invariants

The observe -> reason -> validate -> execute loop should preserve the following invariants.

## Invariant 1: Agent context is sanitized

The reasoning layer receives SanitizedPageState rather than raw Browser PageState.

## Invariant 2: Action plans reference their source state

Every ActionPlan must identify the sanitized_state_id used to generate it. A plan from an older observation must not silently operate on a newer page.

## Invariant 3: Targets are opaque

The agent chooses opaque element IDs. It does not receive or execute CSS selectors, XPath expressions, arbitrary JavaScript, or DevTools commands.

## Invariant 4: Risk is independently derived

The model's declared risk level is advisory input. The policy layer may raise the risk level or block the action based on action type and target context.

## Invariant 5: Stale recovery creates a fresh observation

A stale target triggers a new observation and privacy pass before replanning. The old element ID must not be reused merely because the label looks familiar.

## Invariant 6: Recovery is bounded

The orchestrator stops after its configured recovery limit. Repeatedly refreshing a page until something works is not a safety strategy, despite being a remarkably common human programming technique.

## Invariant 7: Failure is explicit

Contract violations, policy blocks, stale high-risk actions, and execution failures return structured results. The system should fail closed rather than silently continue with uncertain state.

## Invariant 8: Restoration state remains local

Placeholder-to-original mappings belong to the privacy component and are never included in Agent-facing contracts.

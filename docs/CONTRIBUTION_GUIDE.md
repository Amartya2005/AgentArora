# Contribution Guide

AgentArora is organized around a strict privacy boundary. Small changes should preserve that boundary rather than introducing shortcuts that expose raw browser state to the reasoning layer.

## Before changing code

1. Identify which logical member owns the behavior.
2. Read the contract used at that boundary before changing an implementation.
3. Check the existing tests for the affected component.
4. Keep browser execution and raw page data on the local side of the privacy boundary.

## Preferred change pattern

```text
Browser perception
    -> PageState
    -> local privacy processing
    -> SanitizedPageState
    -> reasoning / policy
    -> ActionPlan
    -> browser execution
```

Changes that cross these boundaries should update the relevant contract and tests together. Avoid passing raw page content into agent-facing code merely because it is convenient.

## Validation

For a focused change, run the smallest relevant test set first. Before merging a larger change, run the complete project test suite and verify that contract validation still passes.

Documentation-only changes should still describe the current implementation rather than planned architecture. If a behavior is only a roadmap item, label it as such instead of presenting it as implemented.

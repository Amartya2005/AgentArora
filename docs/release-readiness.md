# Prototype Release Readiness

Use this checklist before presenting a new AgentArora build as a demonstrable prototype.

## Contracts

- [ ] JSON schemas validate all boundary payloads.
- [ ] ActionPlan contains only supported action types.
- [ ] ActionResult uses stable status and error codes.
- [ ] Schema versions are consistent across the loop.

## Privacy

- [ ] Raw sensitive values are removed before reasoning.
- [ ] Independent privacy verification passes.
- [ ] Placeholder mappings remain local.
- [ ] Authentication values are not captured by browser extraction.
- [ ] Sensitive URL path values are sanitized.
- [ ] A session-clear operation removes local restoration state.

## Agent safety

- [ ] Page content is treated as untrusted input.
- [ ] Arbitrary JavaScript is unavailable to the agent.
- [ ] Browser targets are opaque IDs.
- [ ] Risk is recalculated by policy.
- [ ] High-risk actions require the configured confirmation path.

## Dynamic pages

- [ ] Elements are revalidated immediately before execution.
- [ ] Stale low-risk actions follow the bounded recovery path.
- [ ] Stale high-risk actions stop safely.
- [ ] Replanning references a fresh sanitized state.
- [ ] Recovery cannot reuse an obsolete element ID.

## Evidence

- [ ] Unit and regression tests pass.
- [ ] Browser benchmark results are reproducible.
- [ ] Privacy benchmark results identify their dataset and limitations.
- [ ] Performance measurements include environment and workload.
- [ ] Known limitations are documented.

## Presentation rule

Do not claim production readiness solely from a passing prototype test suite. Prototype evidence demonstrates implemented behavior under tested conditions; it does not establish security against every browser, website, model, or deployment environment.

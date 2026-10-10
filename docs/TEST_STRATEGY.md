# Layered Test Strategy

AgentArora should be tested at contract boundaries as well as through complete browser flows. Passing unit tests alone does not establish that the privacy boundary holds end to end.

## Layers
1. **Schema tests:** valid payloads pass; missing, extra, mistyped, and malformed fields behave as specified.
2. **Privacy unit tests:** detection, redaction, URL handling, nested values, and verification are tested independently.
3. **Policy tests:** each action type and risk level has explicit allow, deny, and confirmation cases.
4. **Browser integration tests:** observation, grounding, execution, and result handling work together on controlled pages.
5. **Adversarial tests:** hostile page instructions, stale elements, and misleading labels cannot expand authority.
6. **Regression tests:** each fixed defect becomes a deterministic test.

## Test quality
Use synthetic fixtures, deterministic expectations, and minimal dependencies. Test negative cases as deliberately as successful cases. A test should fail when the safety property it represents is broken, not merely when an implementation detail changes.

## Reporting
Track the scenario, expected result, actual result, and environment. Keep personal data and secrets out of test reports.

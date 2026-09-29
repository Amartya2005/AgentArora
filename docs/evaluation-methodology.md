# Evaluation Methodology

AgentArora should be evaluated as a set of independently testable boundaries rather than as a single end-to-end demo.

## 1. Browser perception

Measure whether the browser layer correctly identifies:

- Visible and enabled interactive elements.
- Accessible names and roles.
- Shadow-DOM content.
- Stable opaque element IDs.
- Elements that become stale between observation and execution.

Record true positives, false positives, false negatives, and extraction failures.

## 2. Privacy detection

Evaluate structured PII and sensitive-context categories separately.

For every category, record:

- True positives.
- False positives.
- False negatives.
- Test-case count.
- Whether the category is value-level or context-level.

Controlled benchmark results should not be presented as universal detection accuracy.

## 3. Redaction precision

Verify that detected sensitive values disappear from Agent-facing payloads while non-sensitive surrounding structure remains usable.

Important checks:

- Raw sensitive values are absent.
- Placeholder mappings remain local.
- Sanitized schemas remain valid.
- Verification flags reflect the actual verification result.

## 4. Agent and policy safety

Test whether generated plans:

- Reference the current sanitized state.
- Use only allowed action types.
- Target opaque element IDs.
- Respect deterministic risk classification.
- Stop when policy requires confirmation.

## 5. Dynamic-DOM recovery

Measure:

- Recovery success for low-risk stale actions.
- Blocking behavior for high-risk stale actions.
- Recovery-attempt bounds.
- Prevention of obsolete element-ID reuse.

## 6. Performance

Report latency and resource usage with the workload, environment, and sample size included. A single local timing measurement is evidence for that environment, not a production performance guarantee.

## Reporting principle

Every benchmark result should state its population, test conditions, and limitations. This keeps the evaluation reproducible and prevents prototype measurements from quietly turning into marketing mythology.

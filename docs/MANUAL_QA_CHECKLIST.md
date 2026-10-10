# Manual QA Checklist

Use controlled pages and synthetic data. Record pass/fail and the browser version for each run.

## Observation
- [ ] A normal page produces a schema-valid page state.
- [ ] Element identifiers are temporary and do not expose sensitive values.
- [ ] Missing or inaccessible elements are handled without crashing.
- [ ] A DOM update triggers fresh grounding before a stale target is used.

## Privacy
- [ ] Synthetic emails and phone numbers are redacted where expected.
- [ ] Authentication and financial contexts receive the intended protection.
- [ ] Nested structures and URL components are covered.
- [ ] Placeholder mappings are not present in agent-facing context.
- [ ] Privacy-verification failure blocks downstream reasoning.

## Planning and execution
- [ ] Malformed action plans are rejected.
- [ ] Unsupported actions are rejected.
- [ ] High-risk actions pause for confirmation.
- [ ] Page content cannot override the user's authorized task.
- [ ] A failed browser bridge produces a clear, sanitized error.

## Reporting
- [ ] No real credentials or personal data appear in logs or screenshots.
- [ ] Each failure includes reproducible steps and expected versus actual behavior.
- [ ] Tests are repeated after changes to schemas, sanitization, policy, or execution.

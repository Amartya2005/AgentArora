# Development Checklist

Use this checklist when changing AgentArora's browser, privacy, reasoning, or execution boundaries.

## Before changing code

- [ ] Identify which member owns the behavior.
- [ ] Check whether a frozen JSON contract is affected.
- [ ] Treat webpage content as untrusted input.
- [ ] Confirm raw sensitive values cannot enter the Agent-facing context.

## Validation

- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Run `pytest -q` for pytest-based tests.
- [ ] Run the relevant browser-extension tests when changing JavaScript.
- [ ] Add regression coverage for the changed behavior.
- [ ] Verify stale-element recovery remains bounded.
- [ ] Verify high-risk actions still require confirmation.

## Before opening a pull request

- [ ] Update the relevant contract or architecture documentation.
- [ ] Record benchmark conditions when reporting performance or detection results.
- [ ] Avoid claiming prototype results establish production-grade security.
- [ ] Review the final diff for secrets, personal data, and unrelated changes.

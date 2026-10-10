# Pre-release Smoke Test

This smoke test is a short gate for a local build. It complements, but does not replace, automated tests and a full security review.

1. Install the extension in a clean test browser profile.
2. Open a controlled page containing ordinary text and synthetic sensitive values.
3. Confirm observation returns a valid page-state contract.
4. Confirm sensitive values are sanitized before any reasoning adapter receives context.
5. Submit an intentionally malformed action plan and verify it is rejected.
6. Change the page after observation and verify stale targets are re-grounded.
7. Trigger a high-risk action and confirm the configured approval gate appears.
8. Simulate a transport failure and confirm execution stops safely.
9. Inspect logs and outputs for accidental raw sensitive values.
10. Remove test data and record the build identifier and outcome.

## Release decision
Do not treat a successful smoke test as proof of production readiness. Record unresolved security, compatibility, and reliability issues explicitly, and do not ship if a known critical privacy-boundary or action-policy failure remains.

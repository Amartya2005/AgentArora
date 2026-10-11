# Regression Test Guidelines

Every bug fix should include a test that fails before the fix and passes afterward. Name tests for behavior, not implementation details. Use synthetic sensitive values and explicit expected sanitized output. Include Unicode and percent-encoded variants when relevant.

When behavior intentionally changes, update the assertion and explain why. Do not weaken assertions simply to make the suite green.
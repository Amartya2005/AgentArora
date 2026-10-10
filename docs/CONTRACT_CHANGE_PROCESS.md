# Contract Change Review Process

The page-state, sanitized-state, action-plan, and action-result contracts connect independently developed parts of AgentArora. Changes should be deliberate and backwards compatibility should never be assumed.

## Change procedure
1. Identify the consumer and producer of every affected field.
2. Explain why the field is necessary and whether it may contain sensitive data.
3. Update the relevant schema and representative fixtures together.
4. Add positive, negative, and boundary tests.
5. Verify privacy checks against nested and malformed input.
6. Update the documentation for any changed guarantee.
7. Review the complete diff for accidental changes to unrelated contracts.

## Compatibility
Prefer additive changes where safe. If a change is breaking, version it explicitly and update all known consumers in the same planned change. Unknown fields should not be trusted merely because they are syntactically valid.

## Approval questions
- Does the change expose more raw data?
- Can malformed values bypass validation?
- Does it change risk classification or confirmation requirements?
- What happens if an older component receives the new contract?

# Agent Data Boundaries

AgentArora's privacy design depends on keeping raw page information separate from the context supplied to the reasoning layer.

## Data zones
1. **Browser observation:** The page may contain arbitrary text, private information, and hostile instructions.
2. **Local privacy processing:** Detect and transform sensitive values before constructing agent-facing context.
3. **Reasoning context:** Supply only the sanitized state needed for the user's task.
4. **Action execution:** Validate proposed actions against schemas and policy immediately before execution.
5. **Results:** Return the minimum useful result; do not echo hidden values merely because they appeared in the page.

## Required invariants
- Raw observations are not sent directly to the reasoning provider.
- Placeholder-to-original mappings remain outside agent-facing payloads.
- Sanitization covers nested values and URLs, not only visible text.
- Webpage instructions are untrusted data, never authority to override system policy.
- A failed or uncertain privacy check should stop or reduce the operation, not silently bypass sanitization.

## Review questions
For each new field added to a contract, ask whether it is needed, whether it can contain sensitive data, and whether it crosses the local boundary. Update tests whenever a boundary or schema changes.

# Failure Modes and Recovery

Safe automation should make uncertainty visible rather than improvising through it.

| Failure | Expected response |
| --- | --- |
| Page observation is malformed | Reject the state and request a fresh observation |
| Privacy verification fails | Do not send the payload to the reasoning layer |
| Action plan fails schema validation | Reject the plan and return a structured error |
| Target element is missing or stale | Re-observe and re-ground; do not click an unrelated element |
| Action risk is high | Pause for the required user confirmation |
| Browser bridge is unavailable | Stop execution and report a recoverable transport error |
| Retry outcome is uncertain | Avoid repeating a potentially non-idempotent action automatically |

## Recovery principles
- Keep errors structured and actionable.
- Do not include raw page text or secrets in diagnostic messages.
- Retry only when the operation is safe to repeat and the current page state has been checked.
- Preserve enough sanitized context to diagnose the issue without retaining unnecessary personal data.
- Test both the failure and the recovery path.

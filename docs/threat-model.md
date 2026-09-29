# AgentArora Threat Model

## Scope

This document describes the primary trust boundaries and abuse cases for the current AgentArora prototype. It focuses on the browser perception, privacy, reasoning, policy, and execution path.

## Assets

The system is designed to protect:

- Personally identifiable information and sensitive page content.
- Authentication values, passwords, OTPs, tokens, and payment data.
- Placeholder-to-original mappings owned by the local privacy layer.
- Browser execution authority.
- The integrity of action-policy decisions.

## Trust boundaries

### Browser -> Privacy Engine

The browser page is treated as untrusted input. Raw PageState may contain values that must never reach the reasoning layer.

### Privacy Engine -> Agent

Only SanitizedPageState is allowed across this boundary. Raw values and restoration mappings remain local to the privacy component.

### Agent -> Policy

The reasoning layer produces structured actions, not executable browser code. Policy validation derives risk independently rather than trusting the model's requested risk level.

### Policy -> Browser

Only validated actions targeting currently valid opaque element IDs may be executed.

## Threats and controls

| Threat | Control |
| --- | --- |
| Sensitive data enters model context | Local sanitization plus independent verification |
| Model attempts arbitrary browser execution | Bounded ActionPlan schema |
| Page text acts as an instruction | Web content is treated as untrusted data |
| Stale target is reused | Pre-execution revalidation and bounded recovery |
| High-risk action is silently retried | Deterministic risk policy and confirmation gates |
| Raw URL path leaks sensitive values | URL path sanitization and bounded decoding |
| Placeholder mapping leaks to agent | Mapping is kept inside the privacy component |

## Residual risks

The prototype does not claim complete protection against every form of prompt injection, novel sensitive identifier, browser compromise, malicious extension, or compromised local host.

The strongest security claims should therefore remain limited to the explicit contracts and controls implemented in the repository.

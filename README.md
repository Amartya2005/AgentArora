# AgentArora

> **Privacy-first browser automation for agentic workflows.**

[![Smart India Hackathon 2026](https://img.shields.io/badge/Smart%20India%20Hackathon-2026-blue)](https://www.sih.gov.in/)
[![Status](https://img.shields.io/badge/status-prototype-orange)](https://github.com/Amartya2005/AgentArora)
[![Privacy](https://img.shields.io/badge/privacy-local%20sanitization-green)](https://github.com/Amartya2005/AgentArora)

## Privacy-Preserving Browser Agent

**Smart India Hackathon 2026**  
**Problem Statement ID:** 26171  
**Theme:** Smart Automation

AgentArora is a privacy-preserving browser automation prototype designed to complete web tasks while reducing unnecessary exposure of sensitive and personally identifiable information (PII).

The core principle is simple:

> **Give the reasoning layer the minimum information required to complete the task, while keeping raw sensitive data inside the local privacy boundary.**

The system separates browser perception, privacy processing, reasoning, action policy, and browser execution into explicit contracts. This makes the privacy boundary testable instead of turning it into another hopeful comment in a README.

---

## Why AgentArora?

Browser agents normally need to inspect the page they are operating on. Real pages can contain much more information than the task actually requires:

- Names, emails, phone numbers, and addresses
- Account, transaction, and payment information
- Passwords, OTPs, API keys, and other authentication data
- Medical information
- Private or confidential communication
- Sensitive values embedded in URLs

Sending the entire page to a reasoning model creates unnecessary exposure.

AgentArora introduces a local privacy layer between browser perception and agent reasoning:

```text
User Task
    ↓
Browser Perception
    ↓
Raw PageState
    ↓
Local Privacy Engine
    ↓
SanitizedPageState
    ↓
Agent / Reasoning Adapter
    ↓
ActionPlan
    ↓
Policy + Validation
    ↓
Browser Execution
    ↓
ActionResult
    ↓
Observe Again / Finish
```

Only the sanitized representation crosses into the Agent-facing context.

---

## ✨ Current Implementation Status

The current `main` branch contains the major prototype pieces from the five-day implementation:

| Area | Status |
| --- | --- |
| Frozen JSON contracts | ✅ |
| PageState schema validation | ✅ |
| Chrome MV3 browser perception | ✅ |
| Opaque browser element IDs | ✅ |
| Accessibility / role / shadow-DOM handling | ✅ |
| Local PII and sensitive-context detection | ✅ |
| Local redaction and placeholder mapping | ✅ |
| Independent privacy verification | ✅ |
| Agent context boundary checks | ✅ |
| Structured action planning | ✅ |
| Action schema validation | ✅ |
| Deterministic action risk policy | ✅ |
| User confirmation for high-risk actions | ✅ |
| Dynamic-DOM stale-element recovery | ✅ |
| Local browser transport bridge | ✅ |
| Authentication-value redaction hardening | ✅ |
| URL path sanitization hardening | ✅ |
| Provider-specific LLM integration | ⏳ Adapter boundary exists; no provider/API key is hard-coded |

The repository is a prototype, not a production-grade browser automation platform. Production deployment would require additional hardening, evaluation, observability, and multi-user security.

---

## 🧠 Architecture

AgentArora is split into three logical members. Each member has a narrow responsibility and communicates through explicit contracts:

### Member 1 — Browser Perception & Execution

Responsibilities:

- Inspect the current webpage using DOM and accessibility information.
- Produce a structured `PageState`.
- Assign temporary opaque element IDs such as `EL_001`.
- Revalidate elements immediately before execution.
- Execute only validated actions from the allowed action set.
- Return sanitized `ActionResult` data.

The browser layer treats webpage content as **untrusted input**. Page text must not become system instructions merely because a website loudly typed it.

### Member 2 — Privacy Engine

Responsibilities:

- Detect PII and sensitive values locally.
- Detect sensitive contexts such as financial, medical, authentication, private communication, and confidential content.
- Replace protected values with controlled placeholders.
- Sanitize URLs and nested content.
- Verify that original sensitive values are not present in the Agent-facing payload.
- Keep placeholder-to-original mappings outside Agent-facing contracts.

### Member 3 — Agent, Policy & Orchestration

Responsibilities:

- Build reasoning context from sanitized state only.
- Produce structured `ActionPlan` objects.
- Validate plans against the frozen action schema.
- Apply deterministic risk classification and policy checks.
- Coordinate the observe → reason → validate → execute loop.
- Trigger fresh observations when the page changes.
- Stop safely when a high-risk stale action cannot be retried automatically.

---

## 🔐 Privacy Boundary

The most important boundary in the system is:

```text
                    LOCAL TRUST BOUNDARY
┌─────────────────────────────────────────────────────┐
│ Browser                                             │
│   ↓                                                 │
│ Raw PageState                                       │
│   ↓                                                 │
│ Privacy Engine                                      │
│   ├── Detection                                     │
│   ├── Redaction                                     │
│   └── Verification                                  │
│   ↓                                                 │
│ SanitizedPageState                                  │
└─────────────────────────────────────────────────────┘
                    ↓
              Agent Reasoning
                    ↓
               ActionPlan
```

### What must not cross the Agent boundary

- Original sensitive values
- Placeholder-to-original mappings
- Passwords or credentials
- Cookies or browser storage
- Authentication tokens
- Arbitrary JavaScript
- Browser DevTools commands
- CSS/XPath selector execution targets
- Unrestricted browser commands

The privacy layer is not a prompt. It is an explicit software boundary with schema validation and independent checks.

---

## 🛡️ Privacy Protection

The detector and tokenizer currently cover structured sensitive data and explicit sensitive-context categories.

### Value-level detection

Examples include:

- Email
- Phone
- Person name
- Address
- Password / OTP values
- Account numbers
- PAN / card-like values
- Payment / currency information
- Message content

### Sensitive-context detection

The current controlled taxonomy includes:

- Financial
- Medical
- Authentication
- Private communication
- Confidential content

Detected values are replaced with stable placeholders, for example:

```text
Raw:
Account Holder: Rahul Sharma
API key: abc123secret
Card: 4111 1111 1111 1111

Sanitized:
Account Holder: [PERSON_01]
API key: [AUTH_01]
Card: [PAN_01]
```

The original-to-placeholder mapping remains local to the privacy component and is not part of the Agent-facing contract.

### URL hardening

The privacy layer also sanitizes sensitive values appearing inside URL paths.

It handles:

- Sensitive path segments
- Encoded path values
- Bounded double-decoding
- Malformed percent-encoded segments
- Query and fragment removal

For example:

```text
https://example.test/profile/Rahul%20Sharma?account=7845129034
```

becomes an Agent-safe representation such as:

```text
https://example.test/profile/[PERSON_01]
```

---

## 🤖 Agent Reasoning Boundary

AgentArora uses an adapter-based reasoning interface:

```text
SanitizedPageState
       ↓
ContextBuilder
       ↓
ReasoningAdapter
       ↓
JSON ActionPlan
       ↓
ActionPlanValidator
       ↓
ActionPolicy
```

The repository does not hard-code OpenAI, Gemini, Anthropic, or another provider.

The current codebase includes a deterministic stub adapter for testing. A future reasoning provider can implement the same `ReasoningAdapter.generate(...)` interface without changing the browser, privacy, or action-policy contracts.

### Context isolation

The Agent context builder rejects forbidden data shapes such as:

- Raw placeholder mappings
- Original-value fields
- Mapping-like structures that could reintroduce protected data

This keeps the reasoning interface intentionally narrow.

---

## ⚙️ Action Model

The initial action vocabulary is deliberately constrained:

| Action | Purpose |
| --- | --- |
| `CLICK` | Click an opaque element |
| `TYPE` | Type a user-approved value into an element |
| `SCROLL` | Scroll the page |
| `SELECT` | Select an option |
| `PRESS_KEY` | Press an allowed keyboard key |
| `WAIT` | Wait for a bounded interval |

An action is represented structurally rather than as executable browser code.

Example:

```json
{
  "action_id": "ACT_continue_001",
  "action_type": "CLICK",
  "target_element_id": "EL_017",
  "reason": "Open the Transactions section",
  "risk_level": "LOW"
}
```

The Agent cannot emit:

- Arbitrary JavaScript
- CSS selectors
- XPath execution targets
- Browser DevTools commands
- Network interception commands
- Unrestricted navigation
- File-system commands

---

## ⚠️ Risk Policy

Action risk is re-evaluated deterministically after plan generation.

Examples:

- A normal low-risk click can remain `LOW`.
- Submit-like actions can be elevated to `HIGH`.
- Typing or selecting into sensitive elements can be elevated to `HIGH`.
- Actions explicitly requiring confirmation are elevated to at least `MEDIUM`.
- High-risk or confirmation-gated actions are not automatically retried after a stale-element failure.

This prevents the reasoning adapter from lowering its own safety requirements by simply returning a conveniently optimistic `risk_level`.

---

## 🔄 Dynamic DOM Recovery

Modern pages mutate while an automation agent is working. A previously captured element can disappear or be replaced before execution.

AgentArora handles this with explicit stale-element recovery:

```text
ActionPlan
   ↓
Element revalidation
   ↓
STALE_ELEMENT
   ↓
Fresh PageState
   ↓
Fresh privacy sanitization
   ↓
New SanitizedPageState
   ↓
Re-plan
```

The current orchestrator:

- Detects stale targets.
- Requests a fresh sanitized observation.
- Ensures the new plan references the new `sanitized_state_id`.
- Prevents reuse of obsolete element IDs.
- Limits stale recovery attempts.
- Stops instead of silently retrying high-risk or confirmation-gated actions.

The default recovery bound is **2 stale recoveries**.

---

## 🌐 Local Browser Transport

The Python side exposes a small localhost bridge between the agent and the Chrome MV3 extension.

Default endpoint:

```text
127.0.0.1:8765
```

The transport carries action plans and action results. `SanitizedPageState` stays outside the browser transport boundary.

This keeps the browser execution channel focused on:

```text
Validated ActionPlan → Browser → ActionResult
```

---

## Data Contracts

The frozen contracts live in `docs/contracts.md` and the `contracts/` directory.

### PageState

Raw browser snapshot passed from Member 1 to Member 2.

Important fields include:

- `page_state_id`
- `captured_at`
- `url`
- `title`
- `visible_text`
- `elements`
- Optional accessibility and visual summaries

### SanitizedPageState

Privacy-processed page state passed from Member 2 to Member 3.

Important fields include:

- `sanitized_state_id`
- `source_page_state_id`
- `url`
- `title`
- `visible_text`
- `elements`
- `privacy_summary`

### ActionPlan

A bounded list of 1–5 structured browser actions.

### ActionResult

Execution outcome returned by the browser layer, including statuses such as:

- `SUCCESS`
- `STALE_ELEMENT`
- `INVALID_ACTION`
- `EXECUTION_FAILED`
- `BLOCKED_BY_POLICY`
- `NEEDS_OBSERVATION`
- `TIMEOUT`

### ErrorDetail

A shared sanitized error representation with stable machine-readable codes.

All boundary payloads use schema version `1.0`.

---

## Chrome MV3 Extension

The `extension/` directory contains the browser-side implementation.

Key pieces include:

```text
extension/
├── manifest.json
├── page-state.js
├── action-handler.js
├── content.js
├── benchmark.js
├── ground-truth.js
├── schemas/
└── README.md
```

### Browser perception capabilities

The extension includes:

- Accessible-name resolution
- ARIA 1.2 role resolution
- Shadow DOM traversal
- Visibility detection
- Enabled-state detection
- Opaque element registry
- WeakRef-based stale element tracking
- Inline PageState validation
- Incremental/diff-oriented page-state support

Passwords are blocked at the extraction layer, and the extension does not capture cookies, tokens, or credentials.

See [`extension/README.md`](extension/README.md) for the browser-specific setup and benchmark details.

---

## 📊 Benchmark & Test Evidence

Validation is intentionally split across browser perception, privacy processing, action policy, and orchestration so failures can be isolated instead of hidden inside one end-to-end test.

The repository contains multiple levels of validation.

### Browser perception benchmark

The extension documents a controlled **39-case ground-truth benchmark** covering browser extraction behavior.

Documented result:

**39 / 39 passed (100%)**

### Privacy detection

The Day 4 controlled dataset documented:

- Existing PII categories: **59 TP, 0 FP, 0 FN**
- New sensitive-context categories in the initial batch: **15 TP, 2 FP, 0 FN**
- After rule calibration, the final controlled sensitive-context cases reported **15 / 15 TP, 0 FP, 0 FN**

These are controlled benchmark results, not a claim of universal PII detection accuracy.

### Representative runtime measurement

One documented local sanitization measurement reported:

| Metric | Value |
| --- | ---: |
| Raw JSON size | 236 bytes |
| Sanitized JSON size | 462 bytes |
| Sanitization time | 1.47 ms |

Sanitized payloads can be larger because they add structural metadata, privacy summaries, and placeholders.

### Regression coverage

The Python test suite covers areas including:

- Contract validation
- Agent plan generation
- Action policy
- Risk classification
- Dynamic-DOM recovery
- Privacy hardening
- URL sanitization
- Authentication-value redaction
- Transport round trips
- Browser action handling

The JavaScript side also contains browser action and regression tests.

---

## 🔒 Security Model

AgentArora follows several explicit security rules:

1. **Webpage content is untrusted.**  
   Page text cannot redefine system policy.

2. **Privacy is enforced before reasoning.**  
   Raw sensitive values do not belong in Agent context.

3. **Actions are constrained.**  
   The Agent cannot generate arbitrary executable browser code.

4. **Targets are opaque.**  
   Element IDs such as `EL_001` do not encode DOM meaning.

5. **Execution uses revalidation.**  
   A previously observed element must still match before it is acted upon.

6. **High-risk actions are confirmation-gated.**  
   Risk is derived again from the action and target instead of trusting the model's label.

7. **Failures fail closed.**  
   Contract, privacy, or policy violations produce bounded failure results instead of silently continuing.

---

## 📁 Repository Layout

```text
AgentArora/
├── agent/
│   ├── agent.py
│   ├── adapters.py
│   ├── context.py
│   ├── dynamic_dom.py
│   ├── policy.py
│   ├── risk_policy.py
│   ├── transport.py
│   └── ...
├── contracts/
│   ├── page-state.schema.json
│   ├── sanitized-page-state.schema.json
│   ├── action-plan.schema.json
│   ├── action-result.schema.json
│   └── shared.schema.json
├── docs/
│   ├── architecture.md
│   ├── contracts.md
│   └── day4-results.md
├── extension/
│   ├── manifest.json
│   ├── page-state.js
│   ├── action-handler.js
│   ├── content.js
│   ├── benchmark.js
│   └── ...
├── src/
│   ├── detector.py
│   ├── privacy_engine.py
│   ├── tokenizer.py
│   └── ...
├── tests/
│   ├── test_agent.py
│   ├── test_task_loop.py
│   ├── test_risk_policy.py
│   ├── test_dynamic_dom.py
│   ├── test_transport.py
│   ├── test_day4_detection.py
│   └── ...
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Python components

The current Python dependency is:

```text
jsonschema>=4.18,<5
```

Create an environment and install the requirements:

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

The Python tests are written primarily with the standard `unittest` framework; the privacy hardening tests also use `pytest`.

For a full local development environment, install:

```bash
pip install pytest
```

Then run the test suite with:

```bash
python -m unittest discover -s tests -v
```

For the pytest-based files:

```bash
pytest -q
```

### Chrome extension

1. Open Chrome and navigate to `chrome://extensions`.
2. Enable **Developer mode**.
3. Choose **Load unpacked**.
4. Select the `extension/` directory.
5. Use the included test page and benchmark described in [`extension/README.md`](extension/README.md).

---

## 📐 Design Against Evaluation Criteria

The prototype is deliberately optimized around the project's evaluation criteria:

| Metric | Weight | Design response |
| --- | ---: | --- |
| Visual context accuracy | 25% | DOM + accessibility structure + optional visual summary |
| Sensitive/PII detection | 20% | Centralized local detector and controlled taxonomy |
| Redaction precision | 20% | Placeholder-based sanitization + independent verification |
| Client-side resource utilization | 20% | Lightweight structured state instead of raw page dumps |
| End-to-end latency | 15% | Compact contracts and a linear observe/reason/act loop |

These percentages come from the project's evaluation criteria, while the implementation decisions are reflected in `docs/architecture.md`.

---

## 🧱 Known Limitations

AgentArora is intentionally a prototype. Current limitations include:

- Detection is heuristic and rule-based rather than exhaustive.
- Unknown sensitive identifiers are not magically inferred.
- URL decoding is intentionally bounded.
- The browser visual representation is lightweight rather than a full visual model.
- The reasoning layer is provider-neutral but no production LLM provider is bundled.
- Browser transport is local and prototype-oriented.
- Persistence, telemetry, authentication, deployment hardening, and multi-user isolation are out of scope.
- A full production-grade prompt-injection defense system is not claimed.

---

## 🗺️ Roadmap

### Completed

- [x] Architecture and trust boundaries
- [x] Frozen JSON contracts
- [x] Browser PageState extraction
- [x] Local privacy sanitization
- [x] Action schema validation
- [x] Deterministic action policy
- [x] Risk-based confirmation
- [x] Dynamic-DOM recovery
- [x] Local browser transport
- [x] URL privacy hardening
- [x] Authentication-value redaction hardening

### Next

- [ ] Production browser-agent runtime
- [ ] Pluggable LLM provider integration
- [ ] Larger, versioned PII evaluation datasets
- [ ] Stronger visual grounding
- [ ] Expanded browser action coverage
- [ ] End-to-end latency/resource benchmarking
- [ ] Deployment and multi-user security hardening

---

## 📚 Documentation

- [Architecture](docs/architecture.md)
- [Common Contracts](docs/contracts.md)
- [Day 4 / privacy hardening results](docs/day4-results.md)
- [Chrome extension documentation](extension/README.md)

---

## 💡 Project Principle

AgentArora is not trying to make the browser agent see everything.

It is trying to make the agent see **enough**.

That distinction is the entire point.

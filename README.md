# Privacy-Preserving Browser Agent — SIH26171

**A Chrome Manifest V3 extension that observes any webpage, extracts a structured semantic snapshot of its interactive elements, and produces a validated `PageState` JSON object — the browser perception layer of a privacy-preserving AI browser agent.**

---

## Problem statement

SIH26171 asks: can a browser agent use full screen/DOM context to automate tasks without sending raw sensitive data to a server?

Standard agentic pipelines ship the entire page — account numbers, names, passwords, transaction history — to a remote model. That is a hard blocker for any privacy-sensitive domain (banking, healthcare, government portals). This project solves it by splitting perception from reasoning: a local browser layer reads and redacts the page; only the sanitized, placeholder-substituted representation travels to the reasoning model.

---

## Architecture

Day 1 implements the leftmost box of the full pipeline:

```
Webpage (any URL)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Member 1 — Browser Agent & Infrastructure  [DAY 1] │
│  Chrome MV3 extension                               │
│  • DOM + accessibility-tree extraction              │
│  • Opaque element IDs  (EL_001, EL_002, …)          │
│  • Local ID → DOM registry (never serialised)       │
│  • Visibility / enabled / bounds detection          │
│  • Password values hard-blocked at source           │
│  • Inline schema validation                         │
│  • Produces: PageState (schema v1.0)                │
└──────────────────┬──────────────────────────────────┘
                   │  PageState  (raw — stays on device)
                   ▼
                 [ Privacy Engine → Agent → Execution ]
                 [ downstream pipeline — not Day 1    ]
```

**Architectural boundary:** `PageState` never leaves the browser in Day 1. No network requests are made. The raw snapshot is the input contract for the downstream privacy engine (Member 2), which owns all PII detection and redaction.

---

## Data contracts

The team uses five frozen JSON Schema (draft 2020-12) files as the immutable cross-member interface. Day 1 touches two of them directly.

| Schema file | Role in Day 1 | Purpose |
|---|---|---|
| [`shared.schema.json`](schemas/shared.schema.json) | Referenced by PageState | Common definitions: `schemaVersion` (`"1.0"`), `opaqueElementId` (`^EL_[0-9]{3,6}$`), `bounds`, `riskLevel`, `actionType`, `errorDetail` |
| [`page-state.schema.json`](schemas/page-state.schema.json) | Produced and validated | Raw page snapshot: URL, title, visible text (≤ 20 000 chars), up to 500 elements each with role/label/text/value/bounds. Passwords, cookies, tokens explicitly excluded by the schema. |

The remaining three schemas (`sanitized-page-state`, `action-plan`, `action-result`) are present in `schemas/` as frozen contracts for downstream members and are not read or produced by Day 1 code.

---

## Day 1 implementation

| Feature | Detail |
|---|---|
| Chrome Manifest V3 extension | `manifest.json`, content scripts only, zero declared permissions beyond `host_permissions: <all_urls>` |
| DOM element extraction | Buttons, links, inputs, textareas, selects, headings h1–h6, labels, ARIA roles via a single `querySelectorAll` pass |
| Opaque element IDs | `EL_001` … `EL_999999`, pattern `^EL_[0-9]{3,6}$`, counter-based, no semantic encoding |
| Local ID → DOM registry | In-memory `Map<string, Element>`, never serialised, reset on each capture |
| Deduplication | `Set`-based; elements matching multiple selectors are registered exactly once |
| Visibility detection | Checks `isConnected`, non-zero `getBoundingClientRect`, `display`, `visibility`, `opacity` |
| Enabled-state detection | Native `disabled` property + `aria-disabled="true"` |
| Bounds | `getBoundingClientRect()` rounded to integer pixels, present only on visible elements |
| Label resolution | Priority chain: `aria-label` → `aria-labelledby` → `<label for>` → wrapping `<label>` → `placeholder` → `title` |
| Role resolution | Explicit `role` attribute → semantic tag map → input-type map |
| Visible text | `TreeWalker` over text nodes, skips `script`/`style`/`noscript` and hidden parents, capped at 20 000 chars |
| Password protection | `<input type="password">` values hard-blocked in both `_text()` and `_value()`; the field is absent from PageState entirely |
| PageState generation | Produces a fully conformant `PageState` object on every page load at `document_idle` |
| Inline schema validator | Structural validator in `page-state.js` checks every constraint from the frozen schema — no external library, no network fetch; logs ✅ / ❌ to the DevTools console |
| Performance logging | Extraction time logged in ms after every capture |

---

## Installation

No build step. The extension is plain JavaScript loaded directly by Chrome.

**Prerequisites:** Chrome or Chromium (any recent version supporting Manifest V3).

```bash
# 1. Clone / download the repo
git clone <repo-url>
cd privacy-browser-agent
```

```
# 2. Open Chrome and navigate to:
chrome://extensions/

# 3. Enable Developer mode (toggle, top-right corner)

# 4. Click "Load unpacked" and select:
privacy-browser-agent/extension/
```

The extension loads immediately with no errors. No npm install, no build, no server required for Day 1.

---

## Usage

### Running the test page

The controlled banking-style test page exercises all 18 test cases (buttons, links, inputs, select, checkbox, headings, disabled control, hidden element, password input, unlabeled input).

**Option A — file:// (simplest)**

```
File → Open File → privacy-browser-agent/test-page/index.html
```

**Option B — local HTTP server (avoids any file:// quirks)**

```bash
# from the privacy-browser-agent/ directory
python -m http.server 8080
# then open:
# http://localhost:8080/test-page/index.html
```

### Inspecting the PageState output

1. Open the test page in Chrome with the extension loaded.
2. Open DevTools → **Console** tab.
3. You will see:

```
=== PRIVACY-PRESERVING BROWSER AGENT ===
PAGE STATE
{
  "schema_version": "1.0",
  "page_state_id": "PS_Xk9mLpQr2w",
  "captured_at": "2026-09-14T10:30:00.000Z",
  "url": "http://localhost:8080/test-page/index.html",
  "title": "SecureBank — Dashboard",
  "visible_text": "SecureBank Dashboard Transactions Profile …",
  "elements": [ … ]
}

[PageState] ✅ Schema validation PASSED

[PageState] Element Registry
  EL_001 → A "Transactions"
  EL_002 → A "Profile"
  EL_003 → A "Support"
  …
```

### Verifying password protection

Open DevTools Console and run:

```js
JSON.stringify(window.__pageStateCapture()).includes("SuperSecret123!")
// must return: false
```

### Inspecting the live registry

```js
window.__elementRegistry.forEach((el, id) => console.log(id, el));
```

---

## Evaluation alignment

| SIH metric | Weight | Day 1 contribution |
|---|---|---|
| Visual context accuracy | 25% | `getBoundingClientRect()` bounds on every visible element; role, label, text, and type captured for all interactive and semantic elements |
| PII detection recall / precision | 20% | PageState carries raw field values (passwords hard-excluded) as the input surface for the downstream privacy engine |
| Redaction precision | 20% | Password values are the one category Member 1 is contractually required to exclude — enforced at two independent code points |
| Client-side resource utilization | 20% | Single `querySelectorAll` pass; no recursive DOM walk; no external dependencies; no on-device AI inference; extraction completes in single-digit ms on the test page |
| End-to-end latency | 15% | Capture runs at `document_idle`; per-capture timing logged to console |

---

## Known limitations

- **Bounds are viewport-relative at capture time.** If the page is scrolled before capture, Y values shift. Page-absolute coordinates require adding `window.scrollY`.
- **Capture runs once at `document_idle`.** SPA navigation (pushState, hash changes) does not trigger a re-capture.
- **Inline validator is structural, not a full JSON Schema 2020-12 engine.** It checks every constraint in the frozen contract but does not implement `$ref` resolution at runtime.
- **`visible_text` is hard-truncated at 20 000 characters** per the schema limit. Very long pages lose trailing text.

---

## Project structure

```
privacy-browser-agent/
│
├── extension/
│   ├── manifest.json       Chrome MV3 manifest — no background worker,
│   │                       content scripts only, zero declared permissions
│   ├── page-state.js       Extraction engine: element registry, visibility,
│   │                       bounds, label resolution, PageState builder,
│   │                       inline schema validator
│   ├── content.js          Orchestrator: runs capture at document_idle,
│   │                       logs PageState + registry to DevTools console
│   └── README.md           Member 1 submodule README (setup + test cases)
│
├── schemas/                Frozen cross-team contracts — DO NOT MODIFY
│   ├── shared.schema.json
│   ├── page-state.schema.json
│   ├── sanitized-page-state.schema.json
│   ├── action-plan.schema.json
│   └── action-result.schema.json
│
└── test-page/
    └── index.html          Controlled banking-style test page with 15+
                            elements covering all 18 Day-1 test cases
                            (fake data, clearly labelled)
```

---

## Team and roles

| Member | Responsibility | Day 1 status |
|---|---|---|
| Member 1 | Browser Agent & Infrastructure — DOM/AX extraction, element ID registry, PageState generation, schema validation | Complete |

---

## Acknowledgements and data sources

- **Chrome Extensions (Manifest V3)** — [developer.chrome.com/docs/extensions/mv3](https://developer.chrome.com/docs/extensions/mv3/)
- **WAI-ARIA Authoring Practices** — role and label resolution follows the ARIA spec accessible-name computation algorithm
- **JSON Schema draft 2020-12** — [json-schema.org](https://json-schema.org/)
- Test page uses entirely **fake data** for prototype purposes. No real financial data is used or stored anywhere.

# Privacy-Preserving Browser Agent — SIH26171

**A Chrome Manifest V3 extension that observes any webpage, extracts a structured semantic snapshot of its interactive elements, and produces a validated `PageState` JSON object — the browser perception layer of a privacy-preserving AI browser agent.**

---

## Problem statement

SIH26171 asks: can a browser agent use full screen/DOM context to automate tasks without sending raw sensitive data to a server?

Standard agentic pipelines ship the entire page — account numbers, names, passwords, transaction history — to a remote model. That is a hard blocker for any privacy-sensitive domain (banking, healthcare, government portals). This project solves it by splitting perception from reasoning: a local browser layer reads and redacts the page; only the sanitized, placeholder-substituted representation travels to the reasoning model.

---

## Architecture

```
Webpage (any URL)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Member 1 — Browser Agent & Infrastructure          │
│  Chrome MV3 extension                               │
│  • DOM + accessibility-tree extraction              │
│  • Open Shadow DOM traversal                        │
│  • Opaque element IDs  (EL_001, EL_002, …)          │
│  • WeakRef element registry (stale-node safe)       │
│  • Visibility / enabled / bounds detection          │
│  • 8-step accessible-name resolution                │
│  • ARIA 1.2 implicit role mapping (39 GT cases)     │
│  • Internal diff engine (cross-capture change det.) │
│  • Password values hard-blocked at source           │
│  • Inline schema validation                         │
│  • Produces: PageState (schema v1.0)                │
└──────────────────┬──────────────────────────────────┘
                   │  PageState  (raw — stays on device)
                   ▼
                 [ Privacy Engine → Agent → Execution ]
                 [ downstream pipeline — not yet impl ]
```

**Architectural boundary:** `PageState` never leaves the browser. No network requests are made. The raw snapshot is the input contract for the downstream privacy engine (Member 2), which owns all PII detection and redaction.

---

## Data contracts

Five frozen JSON Schema (draft 2020-12) files serve as the immutable cross-member interface. The extension produces and validates against two of them.

| Schema file | Role | Purpose |
|---|---|---|
| [`shared.schema.json`](schemas/shared.schema.json) | Referenced by PageState | Common definitions: `schemaVersion` (`"1.0"`), `opaqueElementId` (`^EL_[0-9]{3,6}$`), `bounds`, `riskLevel`, `actionType`, `errorDetail` |
| [`page-state.schema.json`](schemas/page-state.schema.json) | Produced and validated | Raw page snapshot: URL, title, visible text (≤ 20 000 chars), up to 500 elements each with role/label/text/value/bounds. Passwords, cookies, tokens explicitly excluded. |

The remaining three schemas (`sanitized-page-state`, `action-plan`, `action-result`) are present in `schemas/` as frozen contracts for downstream members and are never read or modified by this extension.

---

## Implementation — feature summary

### Element extraction

| Feature | Detail |
|---|---|
| Chrome Manifest V3 | `manifest.json`, content scripts only, zero declared permissions beyond `host_permissions: <all_urls>` |
| SELECTOR | Buttons, links (`a[href]`), inputs (non-hidden), textareas, selects, headings h1–h6, labels, ul, ol, li, option, article, section, summary, and all ARIA role overrides |
| Shadow DOM traversal | `_collectElements(root, results)` recurses into open shadow roots of all descendants; closed roots are intentionally skipped |
| Deduplication | `Set`-based across the full traversal; elements matching multiple selectors or appearing in both light and shadow trees are registered exactly once |

### Element registry

- In-memory `Map<string, WeakRef<Element>>` — never serialised, reset on each capture
- `WeakRef` wrapping allows stale/detached nodes to be detected without memory leaks
- `_resolveRegistryEntry(id)` returns `null` if the node has been GC'd or disconnected
- Pattern enforced: `^EL_[0-9]{3,6}$`

### Accessible-name resolution (8-step priority chain)

| Priority | Source |
|---|---|
| 1 | `aria-label` |
| 2 | `aria-labelledby` (multiple IDs joined; broken refs silently skipped) |
| 3 | `<label for="id">` |
| 4 | Wrapping `<label>` (nested form controls stripped before reading text) |
| 5 | `placeholder` |
| 6 | `title` |
| 7 | `alt` (images, `input[type=image]`) |
| 8 | `aria-describedby` (last-resort fallback) |

All resolved strings are whitespace-normalised and capped at 500 characters.

### Role resolution (ARIA 1.2)

Priority: explicit `role` attribute → native HTML semantic → safe generic fallback.

Notable mappings:

| Tag / condition | Role |
|---|---|
| `<section>` with `aria-label` / `aria-labelledby` / `title` | `region` |
| `<section>` with no accessible name | `generic` |
| `<a href>` | `link` |
| `<a>` without `href` | `generic` |
| `input[type=search]` | `searchbox` |
| `input[type=checkbox]` | `checkbox` |
| `input[type=radio]` | `radio` |
| `input[type=submit\|button\|reset\|image]` | `button` |
| `input[type=range]` | `slider` |
| `<ul>`, `<ol>` | `list` |
| `<li>` | `listitem` |
| `<article>` | `article` |
| `<aside>` | `complementary` |
| `<dialog>` | `dialog` |
| `<details>` | `group` |
| `<summary>` | `button` |
| `<table>` | `table` |
| `<th>` | `columnheader` |
| `<td>` | `cell` |
| `<fieldset>` | `group` |

### Visibility detection

An element is **visible** when ALL of the following hold:

- `el.isConnected === true`
- `getBoundingClientRect()` returns non-zero width AND height
- `computedStyle.display !== 'none'`
- `computedStyle.visibility !== 'hidden'`
- `computedStyle.opacity !== '0'`

### Enabled-state detection

- Native `disabled` property (covers `<input>`, `<button>`, `<select>`, `<textarea>`)
- `aria-disabled="true"` attribute on any element

### Bounds

`getBoundingClientRect()` rounded to integer pixels, viewport-relative, present only on visible elements.

### Password protection

`<input type="password">` values are **never captured**:

- `_text()` returns `""` for password inputs
- `_value()` returns `undefined` for password inputs
- The `value` field is therefore absent from the element entry entirely

### Internal diff engine

Tracks element identity across multiple captures using a `WeakMap<DOMElement, fingerprint>` that is **never reset** between captures (intentional — this is what gives cross-capture identity).

- Fingerprint: `role|label|type|quantisedBounds` (bounds quantised to 8 px grid)
- On each capture, elements are classified as `existing`, `added`, `changed`, or `removed`
- `changed` increments when the same DOM node has a different fingerprint vs. the previous capture
- Result is logged to the console only — never added to `PageState` (frozen schema)

### Schema validation

Inline structural validator (`validatePageState`) checks every constraint from the frozen schema with no external library and no network fetch. Logs `✅ PASSED` or `❌ FAILED` with details to the DevTools console.

---

## Ground-truth benchmark

39 manually authored test cases covering every extraction feature. Run automatically by `benchmark.js` when the extension loads on the test page.

| Range | Area |
|---|---|
| GT-01–GT-11 | Headings, links, label resolution (aria-label, aria-labelledby, `<label for>`, wrapping label, placeholder, title) |
| GT-12–GT-18 | Interactive roles (button, link, combobox, textbox, checkbox, radio) |
| GT-19–GT-22 | Enabled / disabled state |
| GT-23–GT-27 | Visibility (display:none, visibility:hidden, opacity:0, zero-size) |
| GT-28–GT-29 | Password protection |
| GT-30 | `aria-describedby` fallback label |
| GT-31 | `input[type=search]` → `searchbox` role |
| GT-32–GT-33 | `<ul>` → `list`, `<li>` → `listitem` |
| GT-34 | `<article>` → `article` |
| GT-35 | Named `<section>` → `region` |
| GT-36 | Shadow DOM button (open shadow root) |
| GT-37 | `<a>` without `href` → not extracted |
| GT-38 | Broken `aria-labelledby` → placeholder fallback |
| GT-39 | Unnamed `<section>` → `generic` (ARIA 1.2) |

**Current benchmark result: 39/39 — 100% accuracy**

---

## Project structure

```
privacy-browser-agent/
│
├── extension/
│   ├── manifest.json       Chrome MV3 manifest — content scripts only,
│   │                       no background worker, no extra permissions
│   ├── page-state.js       Extraction engine: registry, visibility, bounds,
│   │                       8-step label resolution, ARIA 1.2 role mapping,
│   │                       shadow DOM traversal, diff engine, schema validator
│   ├── content.js          Orchestrator: runs capture at document_idle,
│   │                       logs PageState + registry, runs benchmark
│   ├── ground-truth.js     39 manually authored GT entries (GT-01–GT-39)
│   ├── benchmark.js        Automated benchmark runner — compares extractor
│   │                       output against ground truth, logs pass/fail
│   ├── diff-test.js        Manual diff verification script (not in manifest
│   │                       by default — add temporarily to test diff engine)
│   └── README.md           Member 1 submodule README
│
├── schemas/                Frozen cross-team contracts — DO NOT MODIFY
│   ├── shared.schema.json
│   ├── page-state.schema.json
│   ├── sanitized-page-state.schema.json
│   ├── action-plan.schema.json
│   └── action-result.schema.json
│
├── test-page/
│   ├── index.html          Controlled banking-style test page — 39 GT
│   │                       elements across 7 sections (fake data only)
│   └── ground-truth.js     Mirror of extension/ground-truth.js for the
│                           test page's own script context
│
└── README.md               This file
```

---

## Installation

No build step. The extension is plain JavaScript loaded directly by Chrome.

**Prerequisites:** Chrome or Chromium (any recent version supporting Manifest V3).

```
1. Open Chrome → chrome://extensions/
2. Enable Developer mode (toggle, top-right corner)
3. Click "Load unpacked"
4. Select:  privacy-browser-agent/extension/
```

The extension loads immediately with no errors. No npm install, no build, no server required.

---

## Usage

### Running the test page

**Option A — file:// (simplest)**

```
File → Open File → privacy-browser-agent/test-page/index.html
```

**Option B — local HTTP server (avoids file:// quirks)**

```bash
# from the privacy-browser-agent/ directory
python -m http.server 8080
# then open: http://localhost:8080/test-page/index.html
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
  "title": "SecureBank — Benchmark Page",
  "visible_text": "SecureBank Dashboard Transactions Profile …",
  "elements": [ … ]
}

[PageState] ✅ Schema validation PASSED
[PageState] diff — existing:0 added:N changed:0 removed:0
[PageState] captured N elements in X.Xms

[PageState] Element Registry
  EL_001 → A "Transactions"
  EL_002 → A "Profile"
  …

=== BENCHMARK ===
GT-01 … ✅
GT-02 … ✅
…
GT-39 … ✅
BENCHMARK RESULT: 39/39 passed
```

### Verifying password protection

Open DevTools Console and run:

```js
JSON.stringify(window.__pageStateCapture()).includes("SuperSecret123!")
// must return: false
```

### Inspecting the live registry

```js
window.__elementRegistry.forEach((ref, id) => {
  const el = ref.deref();
  if (el) console.log(id, el.tagName, el.id);
});
```

### Resolving a registry entry by ID

```js
window.__resolveRegistryEntry("EL_001")
// returns the live DOM element, or null if detached
```

### Testing the diff engine

To verify cross-capture change detection, temporarily add `diff-test.js` to the `js` array in `manifest.json` (after `content.js`), reload the extension, and open the test page. The script runs 5 captures (C1–C5), mutates `#el-aria-label` between C2 and C3, and restores it between C3 and C4. Expected console output:

```
[DiffTest] C1 — existing:0  added:N   changed:0 removed:0
[DiffTest] C2 — existing:N  added:0   changed:0 removed:0
[DiffTest] C3 — existing:N-1 added:0  changed:1 removed:0
[DiffTest] C4 — existing:N-1 added:0  changed:1 removed:0
[DiffTest] C5 — existing:N  added:0   changed:0 removed:0
```

Remove `diff-test.js` from the manifest after testing.

---

## Evaluation alignment

| SIH metric | Weight | Contribution |
|---|---|---|
| Visual context accuracy | 25% | `getBoundingClientRect()` bounds on every visible element; role, label, text, and type captured for all interactive and semantic elements; 39-case benchmark at 100% |
| PII detection recall / precision | 20% | PageState carries raw field values (passwords hard-excluded) as the input surface for the downstream privacy engine |
| Redaction precision | 20% | Password values are excluded at two independent code points (`_text()` and `_value()`); no other values are redacted at this layer |
| Client-side resource utilization | 20% | Single `querySelectorAll` pass per root; shadow DOM recursion only where shadow roots exist; no external dependencies; no on-device AI inference |
| End-to-end latency | 15% | Capture runs at `document_idle`; per-capture timing logged to console |

---

## Known limitations

- **Bounds are viewport-relative at capture time.** If the page is scrolled before capture, Y values shift. Page-absolute coordinates require adding `window.scrollY`.
- **Capture runs once at `document_idle`.** SPA navigation (pushState, hash changes) does not trigger a re-capture automatically.
- **Inline validator is structural, not a full JSON Schema 2020-12 engine.** It checks every constraint in the frozen contract but does not implement `$ref` resolution at runtime.
- **`visible_text` is hard-truncated at 20 000 characters** per the schema limit.
- **Closed shadow roots are not traversed** by design — `shadowRoot` returns `null` for closed roots.
- **`--headless=new` blocks extensions.** CDP-based automated testing requires `--headless=old` or headed mode.

---

## Security notes

- No network requests are made by the extension.
- `PageState` never leaves the browser.
- Password values are hard-blocked at the extraction layer.
- The frozen schemas in `schemas/` are never modified.
- No cookies, tokens, or credentials are captured.

---

## Team and roles

| Member | Responsibility |
|---|---|
| Member 1 | Browser Agent & Infrastructure — DOM/AX extraction, element ID registry, PageState generation, schema validation, diff engine, benchmark |

---

## Acknowledgements

- **Chrome Extensions (Manifest V3)** — [developer.chrome.com/docs/extensions/mv3](https://developer.chrome.com/docs/extensions/mv3/)
- **WAI-ARIA 1.2** — role and label resolution follows the ARIA spec accessible-name computation algorithm
- **JSON Schema draft 2020-12** — [json-schema.org](https://json-schema.org/)
- Test page uses entirely **fake data** for prototype purposes. No real financial data is used or stored anywhere.

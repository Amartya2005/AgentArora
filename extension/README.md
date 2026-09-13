# Privacy-Preserving Browser Agent — Day 1

**Member 1 | Browser Perception Layer**
Smart India Hackathon 2026

---

## What This Is

A Chrome Manifest V3 extension that observes a webpage and produces a
**PageState** object conforming exactly to `page-state.schema.json` (schema
version `1.0`).

This is Day 1 only. No PII sanitization, no LLM, no action execution.

---

## Project Structure

```
privacy-browser-agent/
├── extension/
│   ├── manifest.json      Chrome MV3 manifest
│   ├── page-state.js      Extraction engine + inline schema validator
│   ├── content.js         Orchestrator + debug output
│   └── README.md          This file
├── test-page/
│   └── index.html         Controlled banking-style test page (15+ elements)
└── schemas/               Frozen cross-team contracts (DO NOT MODIFY)
    ├── shared.schema.json
    ├── page-state.schema.json
    ├── sanitized-page-state.schema.json
    ├── action-plan.schema.json
    └── action-result.schema.json
```

---

## Setup (Chrome / Chromium)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `extension/` folder
5. The extension loads with no errors

---

## Running the Test Page

**Option A — file:// (simplest)**

Open `test-page/index.html` directly in Chrome:

```
File → Open File → test-page/index.html
```

**Option B — local HTTP server (recommended, avoids some file:// quirks)**

```bash
# Python 3
cd privacy-browser-agent
python -m http.server 8080
# then open: http://localhost:8080/test-page/index.html
```

---

## Inspecting the PageState

1. Open the test page in Chrome with the extension loaded
2. Open DevTools → **Console** tab
3. Look for:

```
=== PRIVACY-PRESERVING BROWSER AGENT ===
PAGE STATE
{ ... }                          ← full PageState JSON
[PageState] ✅ Schema validation PASSED
[PageState] Element Registry
  EL_001 → A "Transactions"
  EL_002 → A "Profile"
  ...
```

The PageState JSON is the raw output that will be passed to Member 2.

---

## PageState Structure

```json
{
  "schema_version": "1.0",
  "page_state_id": "PS_Xk9mLpQr2w",
  "captured_at": "2026-09-14T10:30:00.000Z",
  "url": "http://localhost:8080/test-page/index.html",
  "title": "SecureBank — Dashboard",
  "visible_text": "SecureBank Dashboard Transactions Profile ...",
  "elements": [
    {
      "element_id": "EL_001",
      "role": "link",
      "type": "link",
      "label": "",
      "text": "Transactions",
      "visible": true,
      "enabled": true,
      "bounds": { "x": 100, "y": 16, "width": 100, "height": 32 }
    },
    ...
  ]
}
```

All fields conform to `page-state.schema.json`. No extra fields are added.

---

## Element Registry

`page-state.js` maintains an in-memory `Map<string, Element>`:

```
EL_001 → <a#nav-transactions>
EL_002 → <a#nav-profile>
EL_003 → <a#nav-support>
EL_004 → <h1>
...
```

- IDs are opaque (`EL_NNN`) — they encode no semantic meaning
- IDs are temporary — they reset on each capture
- The registry is browser-local — never serialised or sent anywhere
- Pattern enforced: `^EL_[0-9]{3,6}$`

---

## Visibility Detection

An element is considered **visible** when ALL of the following hold:

- `el.isConnected === true`
- `getBoundingClientRect()` returns non-zero width AND height
- `computedStyle.display !== 'none'`
- `computedStyle.visibility !== 'hidden'`
- `computedStyle.opacity !== '0'`

The hidden button in the test page (`#btn-hidden`) will have `visible: false`.

---

## Enabled State Detection

- Native `disabled` property (covers `<input>`, `<button>`, `<select>`, `<textarea>`)
- `aria-disabled="true"` attribute
- The Export CSV button (`#btn-export`) is `disabled` → `enabled: false`

---

## Bounds

`getBoundingClientRect()` is called for every visible element.
Values are rounded to integers (pixels relative to viewport).

---

## Password Protection

`<input type="password">` values are **never captured**:

- `_text()` returns `""` for password inputs
- `_value()` returns `undefined` for password inputs
- The `value` field is therefore absent from the element entry
- The test page has `#current-password` with `value="SuperSecret123!"` —
  this value will NOT appear anywhere in the PageState

---

## Schema Validation

`page-state.js` includes an inline structural validator (`validatePageState`)
that checks every constraint from the frozen schema:

- `schema_version === "1.0"`
- `page_state_id` matches `^PS_[A-Za-z0-9_-]{6,64}$`
- `captured_at` is a valid date-time string
- `url` length 1–2048
- `title` length ≤ 300
- `visible_text` length ≤ 20000
- `elements` array ≤ 500 items
- Each element: `element_id` matches `^EL_[0-9]{3,6}$`
- Each element: `role` string 1–80 chars
- Each element: `visible` and `enabled` are booleans
- `bounds` fields are numbers, width/height ≥ 0
- No `additionalProperties` on top-level or element objects

Result is logged to the console as ✅ PASSED or ❌ FAILED with details.

---

## Test Cases Covered by the Test Page

| # | Test Case | Element |
|---|-----------|---------|
| 1 | 10+ useful elements | All 15+ elements |
| 2 | Button | `#btn-filter`, `#btn-change-pwd` |
| 3 | Link | `#nav-transactions`, `#nav-profile`, `#nav-support` |
| 4 | Text input | `#search-input` |
| 5 | Labeled input | `#search-input` (has `<label for>`) |
| 6 | Unlabeled input | `#unlabeled-input` (no label, no aria-label) |
| 7 | Select | `#category-select` |
| 8 | Checkbox | `#chk-debits-only` |
| 9 | Heading | `<h1>`, `<h2>` × 3 |
| 10 | Element without text | `#unlabeled-input` |
| 11 | Element without label | `#unlabeled-input` |
| 12 | Disabled control | `#btn-export` (`disabled` attribute) |
| 13 | Hidden element | `#btn-hidden` (inside `display:none` div) |
| 14 | Password input | `#current-password` — value NOT captured |
| 15 | Bounds extraction | All visible elements have `bounds` |
| 16 | Temporary ID format | All IDs match `^EL_[0-9]{3,6}$` |
| 17 | Registry mapping | `__elementRegistry` Map in console |
| 18 | PageState schema validation | Inline validator logs ✅ PASSED |

---

## Acceptance Criteria

- [x] Chrome MV3 extension loads without errors
- [x] Controlled webpage can be inspected
- [x] PageState is generated automatically
- [x] PageState conforms to `page-state.schema.json`
- [x] `schema_version` is exactly `"1.0"`
- [x] `page_state_id` follows `^PS_[A-Za-z0-9_-]{6,64}$`
- [x] `captured_at` is valid ISO 8601
- [x] `url` and `title` are captured
- [x] `visible_text` is captured
- [x] 10+ useful elements are represented
- [x] Every element has a valid opaque `EL_xxx` ID
- [x] `EL_xxx` IDs map locally to actual DOM elements
- [x] `role` is captured
- [x] Visibility is captured
- [x] Enabled state is captured
- [x] Useful labels/text are captured
- [x] Bounds are captured where applicable
- [x] Password values are never captured
- [x] Missing labels/text do not crash the extractor
- [x] No external API/network request is made
- [x] Frozen schemas remain completely unchanged
- [x] README explains setup and testing

---

## Limitations (Day 1)

- Bounds are viewport-relative (not page-absolute); this is correct for
  visual-context use but will shift if the page is scrolled before capture.
- Capture runs once at `document_idle`; dynamic SPA updates are not yet
  observed (Day 2+ concern).
- The inline validator is structural only; it does not use a full JSON Schema
  library (no external dependencies by design).
- `visible_text` is truncated at 20 000 characters per the schema limit.

---

## Security Notes

- No network requests are made by the extension.
- PageState never leaves the browser in Day 1.
- Password values are hard-blocked at the extraction layer.
- The frozen schemas are copied read-only; the originals in
  `PROTOTYPEOFSIH/AgentArora/contracts/` are the canonical source.
